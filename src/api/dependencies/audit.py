from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.audit_repo import AuditRepository
from services.audit_service import AuditService


def get_audit_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AuditRepository:
    return AuditRepository(db)


def get_audit_service(
    audit_repo: AuditRepository = Depends(get_audit_repo),
) -> AuditService:
    return AuditService(audit_repo)
