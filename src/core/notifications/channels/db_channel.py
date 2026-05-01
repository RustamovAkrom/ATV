from services.notifications.notification_service import NotificationService


class DBChannel:
    def __init__(self, service: NotificationService):
        self.service = service

    async def send(self, payload: dict):
        await self.service.create(**payload)
