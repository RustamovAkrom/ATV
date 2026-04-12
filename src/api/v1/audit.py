# src/api/v1/audit.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.audit_repo import AuditRepository
from schemas.audit import AuditSchema

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/", response_model=list[AuditSchema])
async def list_audit_logs(
    limit: int = Query(20, le=100),
    page: int = Query(0),
    db: AsyncSession = Depends(get_db_session),
):
    repo = AuditRepository(db)
    return await repo.list(limit=limit, offset=page * limit)
