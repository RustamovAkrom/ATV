from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies.audit import get_audit_service
from core.cache.decorators import cached
from core.security.rbac.presets import CanViewAudit
from schemas.audit import AuditFilters, AuditSchema, AuditStatsSchema
from schemas.pagination import Page, PaginationParams
from services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit"])

# Делаем проверку прав обязательной для всего роутера сразу,
# чтобы не писать Depends в каждой функции
router.dependencies.append(CanViewAudit)


def get_audit_filters(
    user_id: UUID | None = Query(None),
    request_id: str | None = Query(None),
    method: str | None = Query(None),
    status_code: int | None = Query(None, ge=100, le=599),
    status_min: int | None = Query(None, ge=100, le=599),
    status_max: int | None = Query(None, ge=100, le=599),
    from_date: datetime | None = Query(None, alias="from"),
    to_date: datetime | None = Query(None, alias="to"),
    search: str | None = Query(None),
    is_suspicious: bool | None = Query(None),
) -> AuditFilters:
    return AuditFilters(
        user_id=user_id,
        request_id=request_id,
        method=method,
        status_code=status_code,
        status_min=status_min,
        status_max=status_max,
        from_date=from_date,
        to_date=to_date,
        search=search,
        is_suspicious=is_suspicious,
    )


@router.get("/", response_model=Page[AuditSchema])
@cached(ttl=10, tags=("audit:list",))
async def list_audit_logs(
    filters: AuditFilters = Depends(get_audit_filters),
    pagination: PaginationParams = Depends(),
    service: AuditService = Depends(get_audit_service),
):
    return await service.list_audit_logs(filters, pagination)


@router.get("/recent", response_model=Page[AuditSchema])
@cached(ttl=10, tags=("audit:recent",))
async def recent_audit_logs(
    pagination: PaginationParams = Depends(),
    service: AuditService = Depends(get_audit_service),
):
    return await service.get_recent(pagination)


@router.get("/request/{request_id}", response_model=Page[AuditSchema])
@cached(ttl=10, tags=("audit:request",))
async def get_by_request_id(
    request_id: str,
    pagination: PaginationParams = Depends(),
    service: AuditService = Depends(get_audit_service),
):
    return await service.get_by_request_id(request_id, pagination)


@router.get("/user/{user_id}", response_model=Page[AuditSchema])
@cached(ttl=10, tags=("audit:user",))
async def get_user_audit(
    user_id: UUID,
    pagination: PaginationParams = Depends(),
    service: AuditService = Depends(get_audit_service),
):
    return await service.get_by_user(user_id, pagination)


@router.get("/status/{status_code}", response_model=Page[AuditSchema])
@cached(ttl=10, tags=("audit:status",))
async def get_by_status_code(
    status_code: int,
    pagination: PaginationParams = Depends(),
    service: AuditService = Depends(get_audit_service),
):
    return await service.get_by_status_code(status_code, pagination)


@router.get("/errors", response_model=Page[AuditSchema])
@cached(ttl=10, tags=("audit:errors",))
async def get_recent_errors(
    pagination: PaginationParams = Depends(),
    service: AuditService = Depends(get_audit_service),
):
    return await service.get_errors(pagination)


@router.get("/stats", response_model=AuditStatsSchema)
@cached(ttl=5, tags=("audit:stats",))
async def audit_stats(
    service: AuditService = Depends(get_audit_service),
):
    return await service.get_stats()
