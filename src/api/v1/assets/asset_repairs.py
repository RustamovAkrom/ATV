from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.assets.asset_repair import get_repair_service
from core.cache.decorators import invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac import presets

from schemas.auth import CurrentUserSchema
from schemas.assets.repairs import (
    RepairReportRequest,
    RepairStartRequest,
    RepairCancelRequest,
    RepairSchema,
)

from services.assets.repair_service import RepairService


router = APIRouter(
    prefix="/assets/{asset_id}/repair",
    tags=["Asset Repair"],
)


@router.post(
    "/report",
    response_model=RepairSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def report_asset_repair(
    asset_id: UUID,
    data: RepairReportRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: RepairService = Depends(get_repair_service),
):
    return await service.report_repair(asset_id, data, actor)


@router.post(
    "/{repair_id}/start",
    response_model=RepairSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def start_asset_repair(
    asset_id: UUID,
    repair_id: UUID,
    data: RepairStartRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: RepairService = Depends(get_repair_service),
):
    return await service.start_repair(asset_id, repair_id, data, actor)


@router.post(
    "/{repair_id}/cancel",
    response_model=RepairSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def cancel_asset_repair(
    asset_id: UUID,
    repair_id: UUID,
    data: RepairCancelRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: RepairService = Depends(get_repair_service),
):
    return await service.cancel_repair(asset_id, repair_id, data, actor)
