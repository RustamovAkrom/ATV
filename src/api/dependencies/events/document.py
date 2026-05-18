# api/dependencies/events/document.py
from fastapi import Depends

from api.dependencies.notifications.notification import get_notification_dispatcher
from api.dependencies.assets.asset_history import get_asset_history_service
from api.dependencies.events.base import get_base_event_service
from core.events.document_events import DocumentEventService
from core.notifications.dispatcher import NotificationDispatcher
from api.dependencies.events.base import BaseEventService
from services.assets.asset_history_service import AssetHistoryService


def get_document_event_service(
    base: BaseEventService = Depends(get_base_event_service),
    history: AssetHistoryService = Depends(get_asset_history_service),
    notifications: NotificationDispatcher = Depends(get_notification_dispatcher),
) -> DocumentEventService:
    """DI для DocumentEventService."""
    return DocumentEventService(
        base=base,
        history=history,
        notifications=notifications,
    )
