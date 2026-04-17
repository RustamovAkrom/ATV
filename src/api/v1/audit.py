from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.audit_repo import AuditRepository
from schemas.audit import AuditSchema
from schemas.pagination import PaginationParams

from core.security.auth.types import CurrentUser
from core.security.rbac.presets import IsSuperAdmin


router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/", response_model=list[AuditSchema])
async def list_audit_logs(
    pagination: PaginationParams = Depends(),
    _: CurrentUser = Depends(IsSuperAdmin),
    db: AsyncSession = Depends(get_db_session),
):
    repo = AuditRepository(db)
    return await repo.list(
        limit=pagination.limit,
        offset=pagination.offset(),
    )
