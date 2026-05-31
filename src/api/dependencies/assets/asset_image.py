from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.assets.asset_image_repo import AssetImageRepository
from repositories.assets.asset_repo import AssetRepository
from services.assets.asset_image_service import AssetImageService


def get_asset_image_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetImageRepository:
    """Получить репозиторий для изображений активов."""
    return AssetImageRepository(db)


def get_asset_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetRepository:
    """Получить репозиторий для активов."""
    return AssetRepository(db)


def get_asset_image_service(
    repo: AssetImageRepository = Depends(get_asset_image_repo),
    asset_repo: AssetRepository = Depends(get_asset_repo),
) -> AssetImageService:
    """Get service for asset images management."""
    return AssetImageService(repo, asset_repo)
