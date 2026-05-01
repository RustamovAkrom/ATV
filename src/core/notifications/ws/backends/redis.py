import json
from uuid import UUID

from core.notifications.ws.backends.base import WSBackend


class RedisWSBackend(WSBackend):
    def __init__(self, redis):
        self.redis = redis

    def _channel(self, user_id: UUID) -> str:
        return f"ws:user:{user_id}"

    async def publish(self, user_id: UUID, payload: dict):
        await self.redis.publish(
            self._channel(user_id),
            json.dumps(payload),
        )
