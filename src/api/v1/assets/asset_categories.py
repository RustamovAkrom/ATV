from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies.assets.asset_category import get_asset_category_service
from core.cache.decorators import cached, invalidate_cache
from core.security.rbac.presets import AssetPermissions
from core.slowapi import limiter
from schemas.assets.asset_category import (
    AssetCategoryCreateSchema,
    AssetCategoryOutSchema,
)
from schemas.common import StatusResponse
from services.assets.asset_category_service import AssetCategoryService

router = APIRouter(prefix="/asset-categories", tags=["Asset categories"])


@router.get(
    "/",
    response_model=list[AssetCategoryOutSchema],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(tags=("categories:list",))
async def list_categories(
    service: AssetCategoryService = Depends(get_asset_category_service),
):
    return await service.list()


@router.post(
    "/",
    response_model=AssetCategoryOutSchema,
    dependencies=[Depends(AssetPermissions.CanCreateAssets)],
)
@limiter.limit("20/minute")
@invalidate_cache(tags=("categories:list",))
async def create_category(
    request: Request,
    data: AssetCategoryCreateSchema,
    service: AssetCategoryService = Depends(get_asset_category_service),
):
    return await service.create(data)


@router.delete("/{category_id}")
@limiter.limit("20/minute")
@invalidate_cache(tags=("categories:list",))
async def delete_category(
    request: Request,
    category_id: UUID,
    service: AssetCategoryService = Depends(get_asset_category_service),
):
    await service.delete(category_id)
    return StatusResponse(
        status="deleted", message="Asset category deleted successfully"
    )
