from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.assets.asset_maintenance_repo import AssetMaintenanceRepository
from repositories.assets.asset_repo import AssetRepository
from services.assets.asset_maintenance_service import AssetMaintenanceService
from core.events.asset_events import AssetEventService
from api.dependencies.events.asset import get_asset_event_service


def get_asset_maintenance_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetMaintenanceRepository:
    """Получить репозиторий для техобслуживания"""
    return AssetMaintenanceRepository(db)


def get_asset_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetRepository:
    """Получить репозиторий для активов"""
    return AssetRepository(db)


def get_asset_maintenance_service(
    repo: AssetMaintenanceRepository = Depends(get_asset_maintenance_repo),
    asset_repo: AssetRepository = Depends(get_asset_repo),
    asset_events: AssetEventService = Depends(get_asset_event_service),
) -> AssetMaintenanceService:
    """Получить сервис для техобслуживания"""
    return AssetMaintenanceService(repo, asset_repo, asset_events)
