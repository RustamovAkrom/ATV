from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.warehouse.warehouse_repo import WarehouseRepository
from core.events.warehouse_events import WarehouseEventService
from services.assets.warehouse_service import WarehouseService
from api.dependencies.events.warehouse import get_warehouse_events


def get_warehouse_repo(
    db: AsyncSession = Depends(get_db_session),
) -> WarehouseRepository:
    return WarehouseRepository(db)


def get_warehouse_service(
    repo: WarehouseRepository = Depends(get_warehouse_repo),
    warehouse_events: WarehouseEventService = Depends(get_warehouse_events),

) -> WarehouseService:
    return WarehouseService(
        repo,
        warehouse_events,
)
