from __future__ import annotations
import hashlib, json, os, secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

class PolicyError(Exception): pass
class ApprovalError(Exception): pass

def now(): return datetime.now(timezone.utc).isoformat()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def digest(value): return hashlib.sha256(canonical(value).encode()).hexdigest()
def redacted(value):
    sensitive={"token","password","secret","api_key","authorization","cookie"}
    if isinstance(value, dict): return {str(k): "[REDACTED]" if str(k).lower() in sensitive else redacted(v) for k,v in value.items()}
    if isinstance(value, list): return [redacted(v) for v in value]
    return value

def safe_token(candidate: str|None, expected: str): return bool(candidate and expected and secrets.compare_digest(candidate, expected))

@dataclass
class Task:
    id: str; title: str; prompt: str; tier: str="scrocco"; status: str="pending"; attempts: int=0
    result: dict[str,Any]|None=None; approval_id: str|None=None; created_at: str=field(default_factory=now)

@dataclass
class Approval:
    id: str; task_id: str; payload: dict[str,Any]; payload_hash: str; status: str="pending"
    expires_at: str=field(default_factory=lambda: (datetime.now(timezone.utc)+timedelta(hours=1)).isoformat())

class MemoryRepository:
    """Deterministic test repository; production configuration must use PostgreSQL adapter."""
    def __init__(self): self.tasks={}; self.approvals={}; self.audit=[]; self.kill_switch=False
    async def create_task(self,title,prompt,tier="scrocco",**_):
        import uuid
        t=Task(str(uuid.uuid4()),title,prompt,tier); self.tasks[t.id]=t; self.log(t.id,"task_created",{"tier":tier}); return t
    async def get_task(self, task_id): return self.tasks.get(str(task_id))
    def log(self, task_id,event,data): self.audit.append({"at":now(),"task_id":task_id,"event":event,"data":redacted(data)})

class MockProvider:
    name="mock"
    async def decide(self,prompt): return {"tool":"echo","arguments":{"message":prompt[:2000]},"summary":"mock","rationale":"deterministic"}

class Orchestrator:
    def __init__(self, repo, root: Path, approval_ttl=3600, max_write=65536): self.repo=repo; self.root=root.resolve(); self.ttl=approval_ttl; self.max_write=max_write
    async def run(self, task_id):
        task=await self.repo.get_task(task_id)
        if not task: raise KeyError(task_id)
        if self.repo.kill_switch: raise PolicyError("kill switch attivo")
        decision=await MockProvider().decide(task.prompt); tool=decision["tool"]; args=decision["arguments"]
        if task.tier not in {"scrocco","pro"}: raise PolicyError("tier non valido")
        if task.tier=="scrocco" and tool!="echo": raise PolicyError("tool non consentito")
        if tool=="workspace_write":
            if task.tier!="pro": raise PolicyError("workspace_write richiede pro")
            payload={"tool":tool,"arguments":args}; h=digest(payload)
            if not task.approval_id:
                import uuid
                a=Approval(str(uuid.uuid4()),task.id,payload,h); self.repo.approvals[a.id]=a; task.approval_id=a.id; task.status="awaiting_approval"; self.repo.log(task.id,"approval_requested",{"approval_id":a.id,"payload_hash":h}); return task
            a=self.repo.approvals[task.approval_id]
            if a.status!="approved" or a.payload_hash!=h: raise ApprovalError("approval mancante, scaduta o payload cambiato")
            a.status="consumed"
            rel=args.get("path"); content=args.get("content")
            if not isinstance(rel,str) or not isinstance(content,str) or Path(rel).is_absolute() or ".." in Path(rel).parts: raise PolicyError("percorso non consentito")
            if len(content.encode())>self.max_write: raise PolicyError("contenuto oltre limite")
            dest=(self.root/rel).resolve(); dest.relative_to(self.root); dest.parent.mkdir(parents=True,exist_ok=True); tmp=dest.with_name("."+dest.name+".tmp"); tmp.write_text(content); os.replace(tmp,dest); result={"tool":tool,"path":rel}
        elif tool=="echo": result={"tool":"echo","message":args["message"]}
        else: raise PolicyError("tool non allowlisted")
        task.status="succeeded"; task.result=result; self.repo.log(task.id,"task_succeeded",result); return task
