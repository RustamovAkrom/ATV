# src/core/audit/service.py

from core.database import get_session_factory
from repositories.audit_repo import AuditRepository


async def save_audit_log(data: dict):
    session_factory = get_session_factory()

    async with session_factory() as session:
        repo = AuditRepository(session)

        try:
            await repo.create(data)
            await session.commit()
        except Exception:
            await session.rollback()
