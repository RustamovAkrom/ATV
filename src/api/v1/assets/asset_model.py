from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies.assets.asset_model import get_asset_model_service
from core.cache.decorators import cached, invalidate_cache
from core.security.rbac.presets import ModelsPermissions
from core.slowapi import limiter
from schemas.assets.asset_model import AssetModelCreateSchema, AssetModelOutSchema
from schemas.common import StatusResponse
from services.assets.asset_model_service import AssetModelService

router = APIRouter(prefix="/asset-models", tags=["Asset models"])


@router.get(
    "/",
    response_model=list[AssetModelOutSchema],
    dependencies=[Depends(ModelsPermissions.CanViewModels)],
)
@cached(tags=("model:list",))
async def list_models(service: AssetModelService = Depends(get_asset_model_service)):
    return await service.list()


@router.post(
    "/",
    response_model=AssetModelOutSchema,
    dependencies=[Depends(ModelsPermissions.CanCreateModels)],
)
@limiter.limit("20/minute")
@invalidate_cache(tags=("model:list",))
async def create_model(
    request: Request,
    data: AssetModelCreateSchema,
    service: AssetModelService = Depends(get_asset_model_service),
):
    return await service.create(data)


@router.delete(
    "/{model_id}",
    response_model=StatusResponse,
    dependencies=[Depends(ModelsPermissions.CanDeleteModels)],
)
@limiter.limit("20/minute")
@invalidate_cache(tags=("model:list",))
async def delete_model(
    request: Request,
    model_id: UUID,
    service: AssetModelService = Depends(get_asset_model_service),
):
    await service.delete(model_id)
    return StatusResponse(status="deleted", message="Asset model deleted successfully")
