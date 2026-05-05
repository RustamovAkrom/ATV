from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.organization.region_repo import RegionRepository
from services.organization.region_service import RegionService


def get_region_repo(db: AsyncSession = Depends(get_db_session)) -> RegionRepository:
    return RegionRepository(db)


def get_region_service(
    repo: RegionRepository = Depends(get_region_repo),
) -> RegionService:
    return RegionService(repo)
