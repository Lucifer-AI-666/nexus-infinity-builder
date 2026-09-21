from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from .core import MemoryRepository, Orchestrator, PolicyError, ApprovalError, safe_token

class TaskIn(BaseModel): title: str=Field(min_length=1); prompt: str=Field(min_length=1); tier: str="scrocco"
class DecisionIn(BaseModel): decision: str; reason: str|None=None

def create_app(repo=None):
    repo=repo or MemoryRepository(); app=FastAPI(title="Nexus Infinity",version="0.1.0"); orch=Orchestrator(repo,Path("workspace")); app.state.repo=repo; app.state.orch=orch
    @app.get("/health")
    async def health(): return {"status":"ok"}
    @app.get("/ready")
    async def ready(): return {"status":"ready","database":"memory-demo"}
    @app.post("/v1/tasks")
    async def create(body: TaskIn): return (await repo.create_task(**body.model_dump())).__dict__
    @app.get("/v1/tasks")
    async def list_tasks(): return [t.__dict__ for t in repo.tasks.values()]
    @app.post("/v1/tasks/{task_id}/run")
    async def run(task_id: str):
        try: return (await orch.run(task_id)).__dict__
        except (KeyError,PolicyError,ApprovalError) as e: raise HTTPException(409,str(e))
    @app.get("/v1/approvals")
    async def approvals(): return [a.__dict__ for a in repo.approvals.values()]
    @app.post("/v1/approvals/{approval_id}/decision")
    async def decide(approval_id: str, body: DecisionIn, x_approver_token: str|None=Header(default=None)):
        if not safe_token(x_approver_token,"change-approver-token"): raise HTTPException(403,"token non valido")
        a=repo.approvals.get(approval_id)
        if not a or body.decision not in {"approved","rejected"}: raise HTTPException(409,"decisione non valida")
        a.status=body.decision; repo.log(a.task_id,"approval_decided",{"approval_id":approval_id,"decision":body.decision}); return a.__dict__
    @app.get("/v1/audit")
    async def audit(): return repo.audit
    @app.put("/v1/system/kill-switch")
    async def kill(enabled: bool, x_admin_token: str|None=Header(default=None)):
        if not safe_token(x_admin_token,"change-admin-token"): raise HTTPException(403,"token non valido")
        repo.kill_switch=enabled; repo.log(None,"kill_switch_changed",{"enabled":enabled}); return {"enabled":enabled}
    return app

app=create_app()
