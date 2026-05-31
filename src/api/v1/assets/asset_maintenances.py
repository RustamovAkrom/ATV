from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies.assets.asset_maintenance import get_asset_maintenance_service
from core.cache.decorators import cached, invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import MaintenancesPermissions
from core.slowapi import limiter
from schemas.assets.asset_maintenance import (
    AssetMaintenanceCreateSchema,
    AssetMaintenanceOutSchema,
    AssetMaintenanceUpdateSchema,
)
from schemas.auth import CurrentUserSchema
from schemas.common import StatusResponse
from services.assets.asset_maintenance_service import AssetMaintenanceService

router = APIRouter(
    prefix="/assets/{asset_id}/maintenances", tags=["Asset Maintenances"]
)


@router.get(
    "/",
    response_model=list[AssetMaintenanceOutSchema],
    dependencies=[Depends(MaintenancesPermissions.CanViewMaintenances)],
)
@cached(tags=("maintenance:list",))
async def list_asset_maintenances(
    asset_id: UUID,
    service: AssetMaintenanceService = Depends(get_asset_maintenance_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Список записей технического обслуживания актива"""
    return await service.list_by_asset(asset_id, actor)


@router.post(
    "/",
    response_model=AssetMaintenanceOutSchema,
    dependencies=[Depends(MaintenancesPermissions.CanCreateMaintenances)],
)
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
    """Create maintenance record"""
    return await service.create(asset_id, data, actor)


@router.patch(
    "/{maintenance_id}",
    response_model=AssetMaintenanceOutSchema,
    dependencies=[Depends(MaintenancesPermissions.CanUpdateMaintenances)],
)
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
    """Update maintenance record"""
    return await service.update(maintenance_id, data, actor)


@router.delete(
    "/{maintenance_id}",
    response_model=StatusResponse,
    dependencies=[Depends(MaintenancesPermissions.CanDeleteMaintenances)],
)
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
    """Delete maintenance record"""
    await service.delete(maintenance_id, actor)
    return StatusResponse(
        status="deleted", message="Maintenance record deleted successfully"
    )
