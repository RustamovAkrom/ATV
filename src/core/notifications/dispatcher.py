from typing import Sequence


class NotificationDispatcher:
    def __init__(self, channels: Sequence):
        self.channels = channels

    async def dispatch(self, payload: dict | None):
        if not payload:
            return

        for channel in self.channels:
            try:
                await channel.send(payload)
            except Exception:
                continue
