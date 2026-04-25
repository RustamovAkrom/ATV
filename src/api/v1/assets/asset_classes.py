# api/v1/asset_classes.py

from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.asset_class import get_asset_class_service
from schemas.asset_class import *
from services.asset_class_service import AssetClassService

router = APIRouter(prefix="/asset-classes", tags=["Asset Classes"])


@router.get("/", response_model=list[AssetClassOutSchema])
async def list_classes(service: AssetClassService = Depends(get_asset_class_service)):
    return await service.list()


@router.post("/", response_model=AssetClassOutSchema)
async def create_class(
    data: AssetClassCreateSchema,
    service: AssetClassService = Depends(get_asset_class_service),
):
    return await service.create(data)


@router.delete("/{class_id}")
async def delete_class(
    class_id: UUID,
    service: AssetClassService = Depends(get_asset_class_service),
):
    await service.delete(class_id)
    return {"status": "deleted"}
