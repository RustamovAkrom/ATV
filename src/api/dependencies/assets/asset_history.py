from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.dependencies import get_db_session
from services.assets.asset_history_service import AssetHistoryService
from repositories.assets.asset_history_repo import AssetHistoryRepository


def get_asset_history_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetHistoryRepository:
    return AssetHistoryRepository(db)


def get_asset_history_service(
    repo: AssetHistoryRepository = Depends(get_asset_history_repo),
) -> AssetHistoryService:
    return AssetHistoryService(repo)
