# api/dependencies/asset_class.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.dependencies import get_db_session

from repositories.asset_class_repo import AssetClassRepository
from services.asset_class_service import AssetClassService


def get_asset_class_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetClassRepository:
    return AssetClassRepository(db)


def get_asset_class_service(
    repo: AssetClassRepository = Depends(get_asset_class_repo),
) -> AssetClassService:
    return AssetClassService(repo)
