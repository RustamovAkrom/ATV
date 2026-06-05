"""API endpoints for department management."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from api.dependencies.organizations.departments import get_department_service
from core.cache.decorators import cached, invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import ServicePermissions
from core.slowapi import limiter
from schemas.auth.auth import CurrentUserSchema
from schemas.common import StatusResponse
from schemas.organization.department import (
    DepartmentCreateSchema,
    DepartmentDetailSchema,
    DepartmentOutSchema,
    DepartmentUpdateSchema,
)
from services.organization.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get(
    "/",
    response_model=list[DepartmentOutSchema],
    dependencies=[Depends(ServicePermissions.CanViewServices)],
)
@cached(ttl=30, tags=("department:list",))
async def list_departments(
    region_id: UUID | None = Query(None),
    service_id: UUID | None = Query(None),
    is_active: bool | None = Query(None),
    service: DepartmentService = Depends(get_department_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    return await service.list(region_id, service_id, is_active)


@router.get(
    "/{department_id}",
    response_model=DepartmentDetailSchema,
    dependencies=[Depends(ServicePermissions.CanViewServices)],
)
@cached(ttl=30, tags=("department:detail",))
async def get_department(
    department_id: UUID,
    service: DepartmentService = Depends(get_department_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    return await service.get(department_id)


@router.post(
    "/",
    response_model=DepartmentDetailSchema,
    dependencies=[Depends(ServicePermissions.CanCreateServices)],
)
@limiter.limit("10/minute")
@invalidate_cache(tags=("department:list", "department:detail"))
async def create_department(
    request: Request,
    data: DepartmentCreateSchema,
    service: DepartmentService = Depends(get_department_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    return await service.create(data)


@router.patch(
    "/{department_id}",
    response_model=DepartmentDetailSchema,
    dependencies=[Depends(ServicePermissions.CanUpdateServices)],
)
@limiter.limit("20/minute")
@invalidate_cache(tags=("department:list", "department:detail"))
async def update_department(
    request: Request,
    department_id: UUID,
    data: DepartmentUpdateSchema,
    service: DepartmentService = Depends(get_department_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    return await service.update(department_id, data)


@router.delete(
    "/{department_id}",
    response_model=StatusResponse,
    dependencies=[Depends(ServicePermissions.CanDeleteServices)],
)
@limiter.limit("5/minute")
@invalidate_cache(tags=("department:list", "department:detail"))
async def delete_department(
    request: Request,
    department_id: UUID,
    service: DepartmentService = Depends(get_department_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    await service.delete(department_id)
    return StatusResponse(status="deleted", message="Department deleted successfully")
