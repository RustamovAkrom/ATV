# core/notifications/dispatcher.py
from typing import Sequence


class NotificationDispatcher:
    def __init__(self, channels: Sequence):
        self.channels = channels

    async def dispatch(self, payload: dict | None) -> None:
        """Отправить уведомление через все каналы."""
        if not payload:
            return

        for channel in self.channels:
            try:
                await channel.send(payload)
            except Exception:
                continue  # Логировать ошибку, но не прерывать
