from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.assets.asset_category import get_asset_category_service
from schemas.assets.asset_category import (
    AssetCategoryCreateSchema,
    AssetCategoryOutSchema,
)
from services.assets.asset_category_service import AssetCategoryService
from core.security.rbac.presets import AssetPermissions
from schemas.common import StatusResponse

router = APIRouter(prefix="/asset-categories", tags=["Asset categories"])


@router.get("/", response_model=list[AssetCategoryOutSchema], dependencies=[Depends(AssetPermissions.CanViewAssets)])
async def list_categories(
    service: AssetCategoryService = Depends(get_asset_category_service),
):
    return await service.list()


@router.post("/", response_model=AssetCategoryOutSchema, dependencies=[Depends(AssetPermissions.CanCreateAssets)])
async def create_category(
    data: AssetCategoryCreateSchema,
    service: AssetCategoryService = Depends(get_asset_category_service),
):
    return await service.create(data)


@router.delete("/{category_id}")
async def delete_category(
    category_id: UUID,
    service: AssetCategoryService = Depends(get_asset_category_service),
):
    await service.delete(category_id)
    return StatusResponse(status="deleted", message="Asset category deleted successfully")
