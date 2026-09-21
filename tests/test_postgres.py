import os, pytest
from nexus_infinity.postgres import PostgresRepository, payload_hash

URL=os.getenv('NEXUS_TEST_DATABASE_URL','postgresql+asyncpg://nexus_test:nexus_test@127.0.0.1:5432/nexus_test')

@pytest.mark.asyncio
@pytest.mark.integration
async def test_postgres_approval_hash_and_audit():
    repo=PostgresRepository(URL); await repo.create_schema(); task=await repo.create_task('integration','payload','pro')
    payload={'tool':'workspace_write','arguments':{'path':'a.txt','content':'ok'}}
    approval=await repo.create_approval(task.id,payload); assert approval.payload_hash==payload_hash(payload)
    await repo.decide(approval.id,'approved','tester'); consumed=await repo.consume(approval.id,payload_hash(payload)); assert consumed.status=='consumed'
    await repo.audit(task.id,'secret_test',{'api_key':'hidden'}); await repo.close()
