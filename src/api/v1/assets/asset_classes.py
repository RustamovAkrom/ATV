# api/v1/asset_classes.py

from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.assets.asset_class import get_asset_class_service
from core.security.rbac.presets import AssetPermissions
from schemas.assets.asset_class import AssetClassCreateSchema, AssetClassOutSchema
from services.assets.asset_class_service import AssetClassService
from schemas.common import StatusResponse

router = APIRouter(prefix="/asset-classes", tags=["Asset Classes"])


@router.get("/", response_model=list[AssetClassOutSchema], dependencies=[Depends(AssetPermissions.CanViewAssets)])
async def list_classes(service: AssetClassService = Depends(get_asset_class_service)):
    return await service.list()


@router.post("/", response_model=AssetClassOutSchema, dependencies=[Depends(AssetPermissions.CanCreateAssets)])
async def create_class(
    data: AssetClassCreateSchema,
    service: AssetClassService = Depends(get_asset_class_service),
):
    return await service.create(data)


@router.delete("/{class_id}", response_model=StatusResponse, dependencies=[Depends(AssetPermissions.CanDeleteAssets)])
async def delete_class(
    class_id: UUID,
    service: AssetClassService = Depends(get_asset_class_service),
):
    await service.delete(class_id)
    return StatusResponse(status="deleted", message="Asset class deleted successfully")
