from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies.assets.asset_manufacturer import get_manufacturer_service
from core.cache.decorators import cached, invalidate_cache
from core.slowapi import limiter
from core.security.rbac.presets import ManufacturePermission
from schemas.assets.manufacturer import ManufacturerCreateSchema, ManufacturerOutSchema
from schemas.common import StatusResponse
from services.assets.manufacturer_service import ManufacturerService

router = APIRouter(prefix="/manufacturer", tags=["Manufacturer"])


@router.get(
    "/",
    response_model=list[ManufacturerOutSchema],
    dependencies=[Depends(ManufacturePermission.CanViewManufacture)],
)
@cached(tags=("manufacture:list",))
async def list_manufactures(
    service: ManufacturerService = Depends(get_manufacturer_service),
):
    return await service.list()


@router.post(
    "/",
    response_model=ManufacturerOutSchema,
    dependencies=[Depends(ManufacturePermission.CanCreateManufacture)],
)
@limiter.limit("10/minute")
@invalidate_cache(tags=("manufacture:list",))
async def create_manufacture(
    request: Request,
    data: ManufacturerCreateSchema,
    service: ManufacturerService = Depends(get_manufacturer_service),
):
    return await service.create(data)


@router.delete(
    "/{manufacturer_id}",
    response_model=StatusResponse,
    dependencies=[Depends(ManufacturePermission.CanDeleteManufacture)],
)
@limiter.limit("10/minute")
@invalidate_cache(tags=("manufacture:list",))
async def delete_manufacture(
    request: Request,
    manufacturer_id: UUID,
    service: ManufacturerService = Depends(get_manufacturer_service),
):
    await service.delete(manufacturer_id)
    return StatusResponse(status="deleted", message="Manufacturer deleted successfully")
