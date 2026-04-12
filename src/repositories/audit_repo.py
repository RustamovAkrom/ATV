from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.audit.audit_log import AuditLog


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict):
        self.session.add(AuditLog(**data))

    async def list(self, limit: int, offset: int):
        result = await self.session.execute(
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
