from uuid import UUID

from fastapi import APIRouter, Depends, Query

from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions
from schemas.auth import CurrentUserSchema
from schemas.warehouses.warehouses import (
    WarehouseCreateSchema,
    WarehouseUpdateSchema,
    WarehouseOutSchema,
)
from schemas.pagination import PageOutSchema, PaginationParamsSchema
from services.warehouse.warehouse_service import WarehouseService
from api.dependencies.warehouse import get_warehouse_service

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get(
    "/",
    response_model=PageOutSchema[WarehouseOutSchema],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
async def list_warehouses(
    pagination: PaginationParamsSchema = Depends(),
    region_id: UUID | None = Query(None),
    service: WarehouseService = Depends(get_warehouse_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Список складов с пагинацией и фильтрацией"""
    return await service.list_warehouses(
        page=pagination.page,
        size=pagination.limit,
        region_id=region_id,
    )


@router.post(
    "/",
    response_model=WarehouseOutSchema,
    dependencies=[Depends(AssetPermissions.CanCreateAssets)],
)
async def create_warehouse(
    data: WarehouseCreateSchema,
    service: WarehouseService = Depends(get_warehouse_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Создать новый склад (только для администраторов)"""
    return await service.create_warehouse(data)


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseOutSchema,
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
async def get_warehouse(
    warehouse_id: UUID,
    service: WarehouseService = Depends(get_warehouse_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Получить информацию о складе"""
    return await service.get_warehouse(warehouse_id)


@router.patch(
    "/{warehouse_id}",
    response_model=WarehouseOutSchema,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
async def update_warehouse(
    warehouse_id: UUID,
    data: WarehouseUpdateSchema,
    service: WarehouseService = Depends(get_warehouse_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Обновить информацию о складе"""
    return await service.update_warehouse(warehouse_id, data)


@router.delete(
    "/{warehouse_id}",
    dependencies=[Depends(AssetPermissions.CanDeleteAssets)],
)
async def delete_warehouse(
    warehouse_id: UUID,
    service: WarehouseService = Depends(get_warehouse_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Удалить склад (только если нет активов)"""
    await service.delete_warehouse(warehouse_id)
    return {"message": "Warehouse deleted successfully"}
