from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.assets.asset_history import get_asset_history_service
from api.dependencies.events.base import get_base_event_service
from core.events.asset_events import AssetEventService
from core.events.base import BaseEventService
from db.dependencies import get_db_session
from services.assets.asset_history_service import AssetHistoryService


def get_asset_event_service(
    base: BaseEventService = Depends(get_base_event_service),
    asset_history_service: AssetHistoryService = Depends(get_asset_history_service),
    notification_service: BaseEventService = Depends(get_base_event_service),
) -> AssetEventService:
    return AssetEventService(
        base=base,
        history=asset_history_service,
        notifications=notification_service,
    )
