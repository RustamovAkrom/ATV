from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.asset_category import get_asset_category_service
from schemas.assets.asset_category import (
    AssetCategoryCreateSchema,
    AssetCategoryOutSchema,
)
from services.assets.asset_category_service import AssetCategoryService

router = APIRouter(prefix="/asset-categories", tags=["Asset categories"])


@router.get("/", response_model=list[AssetCategoryOutSchema])
async def list_categories(
    service: AssetCategoryService = Depends(get_asset_category_service),
):
    return await service.list()


@router.post("/", response_model=AssetCategoryOutSchema)
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
    return {"status": "deleted"}
