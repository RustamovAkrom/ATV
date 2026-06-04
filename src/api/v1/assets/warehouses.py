from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from api.dependencies.assets.asset_warehouse import get_warehouse_service
from core.cache.decorators import cached, invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import WarehousePermission
from core.slowapi import limiter
from schemas.assets.warehouses import (
    WarehouseCreateSchema,
    WarehouseOutSchema,
    WarehouseUpdateSchema,
    WarehouseWithDetailsOutSchema,
)
from schemas.auth import CurrentUserSchema
from schemas.common import StatusResponse
from schemas.pagination import PageOutSchema, PaginationParamsSchema
from services.assets.warehouse_service import WarehouseService

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get(
    "/",
    response_model=PageOutSchema[WarehouseOutSchema],
    dependencies=[Depends(WarehousePermission.CanViewWarehouses)],
)
@cached(tags=("warehouse:list",))
async def list_warehouses(
    pagination: PaginationParamsSchema = Depends(),
    department_id: UUID | None = Query(None),
    region_id: UUID | None = Query(None),
    service_id: UUID | None = Query(None),
    is_active: bool | None = Query(None),
    service: WarehouseService = Depends(get_warehouse_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Warehouse list with pagination and filtering"""
    items, total = await service.list_warehouses(
        pagination=pagination,
        department_id=department_id,
        region_id=region_id,
        service_id=service_id,
        is_active=is_active,
    )
    return PageOutSchema(
        items=items, total=total, page=pagination.page, limit=pagination.limit
    )


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseWithDetailsOutSchema,
    dependencies=[Depends(WarehousePermission.CanViewWarehouses)],
)
@cached(tags=("warehouse:detail",))
async def get_warehouse(
    warehouse_id: UUID,
    service: WarehouseService = Depends(get_warehouse_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Get warehouse information"""
    return await service.get_warehouse(warehouse_id)


@router.post(
    "/",
    response_model=WarehouseOutSchema,
    dependencies=[Depends(WarehousePermission.CanCreateWarehouses)],
)
@limiter.limit("10/minute")
@invalidate_cache(tags=("warehouse:list",))
async def create_warehouse(
    request: Request,
    data: WarehouseCreateSchema,
    service: WarehouseService = Depends(get_warehouse_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Создать новый склад"""
    return await service.create_warehouse(data)


@router.patch(
    "/{warehouse_id}",
    response_model=WarehouseOutSchema,
    dependencies=[Depends(WarehousePermission.CanUpdateWarehouses)],
)
@limiter.limit("20/minute")
@invalidate_cache(
    tags=(
        "warehouse:list",
        "warehouse:detail",
    )
)
async def update_warehouse(
    request: Request,
    warehouse_id: UUID,
    data: WarehouseUpdateSchema,
    service: WarehouseService = Depends(get_warehouse_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Update warehouse information"""
    return await service.update_warehouse(warehouse_id, data)


@router.delete(
    "/{warehouse_id}",
    response_model=StatusResponse,
    dependencies=[Depends(WarehousePermission.CanDeleteWarehouses)],
)
@limiter.limit("5/minute")
@invalidate_cache(
    tags=(
        "warehouse:list",
        "warehouse:detail",
    )
)
async def delete_warehouse(
    request: Request,
    warehouse_id: UUID,
    service: WarehouseService = Depends(get_warehouse_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Удалить склад (только если нет активов)"""
    await service.delete_warehouse(warehouse_id)
    return StatusResponse(status="deleted", message="Warehouse deleted successfully")
