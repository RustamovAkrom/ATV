from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.assets.warehouse_repo import WarehouseRepository
from repositories.assets.asset_repo import AssetRepository
from core.events.warehouse_events import WarehouseEventService
from services.assets.warehouse_service import WarehouseService
from api.dependencies.events.warehouse import get_warehouse_event_service
from api.dependencies.assets.asset import get_asset_repo

def get_warehouse_repo(
    db: AsyncSession = Depends(get_db_session),
) -> WarehouseRepository:
    return WarehouseRepository(db)


def get_warehouse_service(
    repo: WarehouseRepository = Depends(get_warehouse_repo),
    warehouse_events: WarehouseEventService = Depends(get_warehouse_event_service),
    asset_repo: AssetRepository = Depends(get_asset_repo),
) -> WarehouseService:
    return WarehouseService(
        repo,
        asset_repo,
        warehouse_events,
)
