from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone, timedelta
from typing import Any
from uuid import UUID, uuid4
from sqlalchemy import DateTime, Integer, JSON, String, Text, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TaskRow(Base):
    __tablename__ = "tasks"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(240))
    prompt: Mapped[str] = mapped_column(Text)
    tier: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    approval_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class ApprovalRow(Base):
    __tablename__ = "approvals"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    payload_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="pending")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    decided_by: Mapped[str | None] = mapped_column(String(128), nullable=True)

class AuditRow(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[UUID | None] = mapped_column(nullable=True)
    event: Mapped[str] = mapped_column(String(128))
    data: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

def payload_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode()).hexdigest()

def _safe(value: Any) -> Any:
    sensitive = {"token", "password", "secret", "api_key", "authorization", "cookie"}
    if isinstance(value, dict):
        return {k: "[REDACTED]" if k.lower() in sensitive else _safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_safe(v) for v in value]
    return value

class PostgresRepository:
    def __init__(self, url: str):
        self.engine = create_async_engine(url, pool_pre_ping=True)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)

    async def create_schema(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def create_task(self, title: str, prompt: str, tier: str = "scrocco") -> TaskRow:
        async with self.sessions() as session, session.begin():
            row = TaskRow(title=title, prompt=prompt, tier=tier)
            session.add(row)
            await session.flush()
            await self._audit(session, row.id, "task_created", {"tier": tier})
            return row

    async def get_task(self, task_id: UUID | str) -> TaskRow | None:
        async with self.sessions() as session:
            return await session.get(TaskRow, UUID(str(task_id)))

    async def create_approval(self, task_id: UUID | str, payload: dict[str, Any]) -> ApprovalRow:
        approval = ApprovalRow(
            task_id=UUID(str(task_id)),
            payload=payload,
            payload_hash=payload_hash(payload),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        async with self.sessions() as session, session.begin():
            session.add(approval)
            await session.flush()
            return approval

    async def decide(self, approval_id: UUID | str, decision: str, actor: str) -> ApprovalRow:
        async with self.sessions() as session, session.begin():
            row = await session.scalar(select(ApprovalRow).where(ApprovalRow.id == UUID(str(approval_id))).with_for_update())
            if row is None or row.status != "pending" or row.expires_at <= datetime.now(timezone.utc):
                raise ValueError("approval non disponibile")
            if decision not in {"approved", "rejected"}:
                raise ValueError("decisione non valida")
            row.status, row.decided_by = decision, actor
            return row

    async def consume(self, approval_id: UUID | str, expected_hash: str) -> ApprovalRow:
        async with self.sessions() as session, session.begin():
            row = await session.scalar(select(ApprovalRow).where(ApprovalRow.id == UUID(str(approval_id))).with_for_update())
            if row is None or row.status != "approved" or row.payload_hash != expected_hash or row.expires_at <= datetime.now(timezone.utc):
                raise ValueError("approval non valida")
            row.status = "consumed"
            return row

    async def audit(self, task_id: UUID | str | None, event: str, data: dict[str, Any]) -> None:
        async with self.sessions() as session, session.begin():
            await self._audit(session, UUID(str(task_id)) if task_id else None, event, data)

    async def _audit(self, session, task_id, event, data) -> None:
        session.add(AuditRow(task_id=task_id, event=event, data=_safe(data)))

    async def close(self) -> None:
        await self.engine.dispose()
