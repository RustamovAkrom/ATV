from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies.assets.asset_maintenance import get_asset_maintenance_service
from core.cache.decorators import cached, invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.slowapi import limiter
from schemas.assets.asset_maintenance import (
    AssetMaintenanceCreateSchema,
    AssetMaintenanceOutSchema,
    AssetMaintenanceUpdateSchema,
)
from schemas.auth import CurrentUserSchema
from services.assets.asset_maintenance_service import AssetMaintenanceService

router = APIRouter(
    prefix="/assets/{asset_id}/maintenances", tags=["Asset Maintenances"]
)


@router.get("/", response_model=list[AssetMaintenanceOutSchema])
@cached(tags=("maintenance:list",))
async def list_asset_maintenances(
    asset_id: UUID,
    service: AssetMaintenanceService = Depends(get_asset_maintenance_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Список записей технического обслуживания актива"""
    return await service.list_by_asset(asset_id, actor)


@router.post("/", response_model=AssetMaintenanceOutSchema)
@limiter.limit("20/minute")
@invalidate_cache(
    tags=(
        "assets:list",
        "assets:detail",
        "maintenance:list",
    )
)
async def create_asset_maintenance(
    request: Request,
    asset_id: UUID,
    data: AssetMaintenanceCreateSchema,
    service: AssetMaintenanceService = Depends(get_asset_maintenance_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Создать запись о техническом обслуживании"""
    return await service.create(asset_id, data, actor)


@router.patch("/{maintenance_id}", response_model=AssetMaintenanceOutSchema)
@limiter.limit("20/minute")
@invalidate_cache(
    tags=(
        "assets:list",
        "assets:detail",
        "maintenance:list",
    )
)
async def update_asset_maintenance(
    request: Request,
    asset_id: UUID,
    maintenance_id: UUID,
    data: AssetMaintenanceUpdateSchema,
    service: AssetMaintenanceService = Depends(get_asset_maintenance_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Обновить запись о техническом обслуживании"""
    return await service.update(maintenance_id, data, actor)


@router.delete("/{maintenance_id}")
@limiter.limit("10/minute")
@invalidate_cache(
    tags=(
        "assets:list",
        "assets:detail",
        "maintenance:list",
    )
)
async def delete_asset_maintenance(
    request: Request,
    asset_id: UUID,
    maintenance_id: UUID,
    service: AssetMaintenanceService = Depends(get_asset_maintenance_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Удалить запись о техническом обслуживании"""
    await service.delete(maintenance_id, actor)
    return {"status": "deleted", "message": "Maintenance record deleted successfully"}
