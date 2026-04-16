from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.audit_repo import AuditRepository


def get_audit_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AuditRepository:
    return AuditRepository(db)
