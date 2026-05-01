from fastapi import Depends


from api.dependencies.assets.asset_history import get_asset_history_service
from api.dependencies.events.base import get_base_event_service
from api.dependencies.notifications.notification import get_notification_dispatcher
from core.events.base import BaseEventService
from core.notifications.dispatcher import NotificationDispatcher
from services.assets.asset_history_service import AssetHistoryService
from core.events.repair_events import RepairEventService


def get_asset_repair_event_service(
    base: BaseEventService = Depends(get_base_event_service),
    asset_history_service: AssetHistoryService = Depends(get_asset_history_service),
    notification_dispatcher: NotificationDispatcher = Depends(
        get_notification_dispatcher
    ),
) -> RepairEventService:
    return RepairEventService(
        base=base,
        history=asset_history_service,
        notifications=notification_dispatcher,
    )
