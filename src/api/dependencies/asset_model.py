from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.dependencies import get_db_session

from repositories.asset_model_repo import AssetModelRepository
from repositories.manufacturer_repo import ManufacturerRepository
from repositories.asset_category_repo import AssetCategoryRepository
from services.asset_model_service import AssetModelService

from .manufacturer import get_manufacturer_repo
from .asset_category import get_asset_category_repo


def get_asset_model_repo(
    db: AsyncSession = Depends(get_db_session)
) -> AssetModelRepository:
    return AssetModelRepository(db)


def get_asset_model_service(
    repo: AssetModelRepository = Depends(get_asset_model_repo),
    manufacturer_repo: ManufacturerRepository = Depends(get_manufacturer_repo),
    category_repo: AssetCategoryRepository = Depends(get_asset_category_repo)
) -> AssetModelService:
    return AssetModelService(
        repo,
        manufacturer_repo,
        category_repo
    )
