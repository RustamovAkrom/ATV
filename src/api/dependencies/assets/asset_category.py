from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.assets.asset_category_repo import AssetCategoryRepository
from services.assets.asset_category_service import AssetCategoryService


def get_asset_category_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetCategoryRepository:
    return AssetCategoryRepository(db)


def get_asset_category_service(
    repo: AssetCategoryRepository = Depends(get_asset_category_repo),
) -> AssetCategoryService:
    return AssetCategoryService(repo)
