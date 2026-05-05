from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.assets.asset_warehouse import get_warehouse_service
from api.dependencies.assets.assets import get_asset_service
from core.cache.decorators import invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions

from schemas.auth import CurrentUserSchema
from schemas.assets.warehouses import WarehouseMoveRequest
from schemas.assets.assets import AssetDetailSchema

from services.assets.warehouse_service import WarehouseService
from services.assets.asset_service import AssetService


router = APIRouter(
    prefix="/assets/{asset_id}/warehouse",
    tags=["Asset Warehouse"],
)


@router.post(
    "/",
    response_model=AssetDetailSchema,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@invalidate_cache(tags=("assets:list",))
async def move_asset_to_warehouse(
    asset_id: UUID,
    data: WarehouseMoveRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: WarehouseService = Depends(get_warehouse_service),
    asset_service: AssetService = Depends(get_asset_service),
):
    await service.move_asset_to_warehouse(asset_id, data, actor)
    return await asset_service.get(asset_id, actor)
