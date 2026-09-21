import pytest
from pathlib import Path
from nexus_infinity.core import MemoryRepository, Orchestrator, PolicyError

@pytest.mark.asyncio
async def test_scrocco_echo_and_audit(tmp_path: Path):
    repo=MemoryRepository(); flow=Orchestrator(repo,tmp_path); task=await repo.create_task("t","ciao")
    done=await flow.run(task.id)
    assert done.status == "succeeded"
    assert done.result == {"tool":"echo","message":"ciao"}
    assert repo.audit[-1]["event"] == "task_succeeded"

@pytest.mark.asyncio
async def test_kill_switch_blocks(tmp_path: Path):
    repo=MemoryRepository(); repo.kill_switch=True; flow=Orchestrator(repo,tmp_path); task=await repo.create_task("t","ciao")
    with pytest.raises(PolicyError): await flow.run(task.id)

@pytest.mark.asyncio
async def test_sensitive_audit_is_redacted(tmp_path: Path):
    repo=MemoryRepository(); repo.log("t","x",{"api_key":"secret","nested":{"token":"bad"}})
    assert repo.audit[-1]["data"] == {"api_key":"[REDACTED]","nested":{"token":"[REDACTED]"}}
