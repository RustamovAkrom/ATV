from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.asset_model import get_asset_model_service
from schemas.assets.asset_model import AssetModelCreateSchema, AssetModelOutSchema
from services.assets.asset_model_service import AssetModelService

router = APIRouter(prefix="/asset-models", tags=["Asset models"])


@router.get("/", response_model=list[AssetModelOutSchema])
async def list_models(service: AssetModelService = Depends(get_asset_model_service)):
    return await service.list()


@router.post("/", response_model=AssetModelOutSchema)
async def create_model(
    data: AssetModelCreateSchema,
    service: AssetModelService = Depends(get_asset_model_service),
):
    return await service.create(data)


@router.delete("/{model_id}")
async def delete_model(
    model_id: UUID,
    service: AssetModelService = Depends(get_asset_model_service),
):
    return await service.delete(model_id)
