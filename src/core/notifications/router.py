class NotificationRouter:
    def __init__(self, channels: list):
        self.channels = channels

    async def dispatch(self, payload: dict):
        for channel in self.channels:
            try:
                await channel.send(payload)
            except Exception:
                continue
