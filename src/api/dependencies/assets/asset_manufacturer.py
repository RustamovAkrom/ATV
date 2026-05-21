from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.assets.manufacturer_repo import ManufacturerRepository
from services.assets.manufacturer_service import ManufacturerService


def get_manufacturer_repo(
    db: AsyncSession = Depends(get_db_session),
) -> ManufacturerRepository:
    return ManufacturerRepository(db)


def get_manufacturer_service(
    repo: ManufacturerRepository = Depends(get_manufacturer_repo),
) -> ManufacturerService:
    return ManufacturerService(repo)
