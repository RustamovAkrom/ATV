# core/events/domain_event_service.py
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

from core.events.base import BaseEventService
from core.notifications.dispatcher import NotificationDispatcher
from services.assets.asset_history_service import AssetHistoryService


class DomainEventService:
    """
    Базовый класс для всех доменных event сервисов.
    Убирает дублирование history и notifications во всех наследниках.
    """

    def __init__(
        self,
        base: BaseEventService,
        history: AssetHistoryService,
        notifications: NotificationDispatcher,
    ):
        self.base = base
        self.history = history
        self.notifications = notifications

    async def _execute(
        self,
        *,
        asset_id: UUID,
        actor_id: UUID,
        action: str,
        description: str,
        audit_event: str,
        audit_payload: dict | None = None,
        notification: Callable[[], Awaitable[Any]] | None = None,
    ):
        """Универсальный метод для всех событий."""
        await self.base.execute(
            history=lambda: self.history.log(asset_id, actor_id, action, description),
            audit_event=audit_event,
            audit_payload=audit_payload or {},
            notification=notification,
        )
