# api/dependencies/events/transfer.py
from fastapi import Depends

from api.dependencies.assets.asset_history import get_asset_history_service
from api.dependencies.events.base import get_base_event_service
from api.dependencies.notifications.notification import get_notification_dispatcher
from core.events.base import BaseEventService
from core.events.transfer_events import TransferEventService
from core.notifications.dispatcher import NotificationDispatcher
from services.assets.asset_history_service import AssetHistoryService


def get_transfer_event_service(
    base: BaseEventService = Depends(get_base_event_service),
    history: AssetHistoryService = Depends(get_asset_history_service),
    notifications: NotificationDispatcher = Depends(get_notification_dispatcher),
) -> TransferEventService:
    """DI для TransferEventService."""
    return TransferEventService(
        base=base,
        history=history,
        notifications=notifications,
    )
