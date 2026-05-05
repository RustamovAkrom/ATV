from fastapi import Depends

from services.assets.asset_history_service import AssetHistoryService
from core.events.transfer_events import TransferEventService
from core.events.base import BaseEventService
from api.dependencies.events.base import get_base_event_service
from api.dependencies.assets.asset_history import get_asset_history_service
from api.dependencies.notifications.notification import get_notification_dispatcher
from core.notifications.dispatcher import NotificationDispatcher


def get_asset_transfer_events(
    base: BaseEventService = Depends(get_base_event_service),
    asset_history_service: AssetHistoryService = Depends(get_asset_history_service),
    notification_dispatcher: NotificationDispatcher = Depends(
        get_notification_dispatcher
    ),
) -> TransferEventService:
    return TransferEventService(
        base=base,
        history=asset_history_service,
        notifications=notification_dispatcher,
    )
