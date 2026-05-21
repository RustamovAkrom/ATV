from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.assets.asset_manufacturer import get_manufacturer_service
from schemas.assets.manufacturer import ManufacturerCreateSchema, ManufacturerOutSchema
from services.assets.manufacturer_service import ManufacturerService
from schemas.common import StatusResponse

router = APIRouter(prefix="/manufacturer", tags=["Manufacturer"])


@router.get("/", response_model=list[ManufacturerOutSchema])
async def list_manufactures(
    service: ManufacturerService = Depends(get_manufacturer_service),
):
    return await service.list()


@router.post("/", response_model=ManufacturerOutSchema)
async def create_manufacture(
    data: ManufacturerCreateSchema,
    service: ManufacturerService = Depends(get_manufacturer_service),
):
    return await service.create(data)


@router.delete("/{manufacturer_id}", response_model=StatusResponse)
async def delete_manufacture(
    manufacturer_id: UUID,
    service: ManufacturerService = Depends(get_manufacturer_service),
):
    await service.delete(manufacturer_id)
    return StatusResponse(status="deleted", message="Manufacturer deleted successfully")
