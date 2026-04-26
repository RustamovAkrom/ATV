from services.notifications.notification_service import NotificationService


class NotificationDispatcher:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    async def dispatch(self, payload: dict):
        try:
            await self.notification_service.create(**payload)
        except Exception:
            # NEVER ломаем бизнес-логику
            pass
