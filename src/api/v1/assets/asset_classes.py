# api/v1/asset_classes.py

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies.assets.asset_class import get_asset_class_service
from core.cache.decorators import cached, invalidate_cache
from core.security.rbac.presets import ClassesPermissions
from core.slowapi import limiter
from schemas.assets.asset_class import AssetClassCreateSchema, AssetClassOutSchema
from schemas.common import StatusResponse
from services.assets.asset_class_service import AssetClassService

router = APIRouter(prefix="/asset-classes", tags=["Asset Classes"])


@router.get(
    "/",
    response_model=list[AssetClassOutSchema],
    dependencies=[Depends(ClassesPermissions.CanViewClasses)],
)
@cached(tags=("classes:list",))
async def list_classes(service: AssetClassService = Depends(get_asset_class_service)):
    return await service.list()


@router.post(
    "/",
    response_model=AssetClassOutSchema,
    dependencies=[Depends(ClassesPermissions.CanCreateClasses)],
)
@limiter.limit("20/minute")
@invalidate_cache(tags=("classes:list",))
async def create_class(
    request: Request,
    data: AssetClassCreateSchema,
    service: AssetClassService = Depends(get_asset_class_service),
):
    return await service.create(data)


@router.delete(
    "/{class_id}",
    response_model=StatusResponse,
    dependencies=[Depends(ClassesPermissions.CanDeleteClasses)],
)
@limiter.limit("20/minute")
@invalidate_cache(tags=("classes:list",))
async def delete_class(
    request: Request,
    class_id: UUID,
    service: AssetClassService = Depends(get_asset_class_service),
):
    await service.delete(class_id)
    return StatusResponse(status="deleted", message="Asset class deleted successfully")
