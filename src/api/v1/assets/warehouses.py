from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from api.dependencies.assets.asset_warehouse import get_warehouse_service
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions
from core.slowapi import limiter
from schemas.assets.warehouses import (
    WarehouseCreateSchema,
    WarehouseOutSchema,
    WarehouseUpdateSchema,
    WarehouseWithDetailsOutSchema,
)
from schemas.auth import CurrentUserSchema
from schemas.pagination import PageOutSchema, PaginationParamsSchema
from services.assets.warehouse_service import WarehouseService

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


# ========== GET запросы (без rate limit) ==========


@router.get(
    "/",
    response_model=PageOutSchema[WarehouseOutSchema],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
async def list_warehouses(
    pagination: PaginationParamsSchema = Depends(),
    region_id: UUID | None = Query(None),
    service_id: UUID | None = Query(None),
    is_active: bool | None = Query(None),
    service: WarehouseService = Depends(get_warehouse_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Список складов с пагинацией и фильтрацией"""
    items, total = await service.list_warehouses(
        pagination=pagination,
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
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
async def get_warehouse(
    warehouse_id: UUID,
    service: WarehouseService = Depends(get_warehouse_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Получить информацию о складе"""
    return await service.get_warehouse(warehouse_id)


# ========== POST/PATCH/DELETE запросы (с rate limit) ==========


@router.post(
    "/",
    response_model=WarehouseOutSchema,
    dependencies=[Depends(AssetPermissions.CanCreateAssets)],
)
@limiter.limit("10/minute")
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
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@limiter.limit("20/minute")
async def update_warehouse(
    request: Request,
    warehouse_id: UUID,
    data: WarehouseUpdateSchema,
    service: WarehouseService = Depends(get_warehouse_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Обновить информацию о складе"""
    return await service.update_warehouse(warehouse_id, data)


@router.delete(
    "/{warehouse_id}",
    response_model=dict[str, str],
    dependencies=[Depends(AssetPermissions.CanDeleteAssets)],
)
@limiter.limit("5/minute")
async def delete_warehouse(
    request: Request,
    warehouse_id: UUID,
    service: WarehouseService = Depends(get_warehouse_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Удалить склад (только если нет активов)"""
    await service.delete_warehouse(warehouse_id)
    return {"message": "Warehouse deleted successfully"}
