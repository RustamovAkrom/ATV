import asyncio
import json
from collections.abc import AsyncGenerator

from core.config import get_settings
from core.redis import redis_client

settings = get_settings()
CHANNEL = "audit_stream"


class MemoryAuditStream:
    def __init__(self):
        self.subscribers: set[asyncio.Queue] = set()

    async def publish(self, event: dict) -> None:
        if not self.subscribers:
            return

        for queue in list(self.subscribers):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                continue

    async def subscribe(self) -> AsyncGenerator[dict, None]:
        queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self.subscribers.add(queue)

        try:
            while True:
                yield await queue.get()
        finally:
            self.subscribers.discard(queue)


class RedisAuditStream:
    async def publish(self, event: dict) -> None:
        await redis_client.publish(CHANNEL, json.dumps(event, ensure_ascii=False))

    async def subscribe(self) -> AsyncGenerator[dict, None]:
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(CHANNEL)

        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue

                data = message.get("data")
                if isinstance(data, bytes):
                    data = data.decode("utf-8")

                try:
                    yield json.loads(data)
                except Exception:
                    continue
        finally:
            try:
                await pubsub.unsubscribe(CHANNEL)
            finally:
                close = getattr(pubsub, "aclose", None) or getattr(
                    pubsub, "close", None
                )
                if close is not None:
                    result = close()
                    if asyncio.iscoroutine(result):
                        await result


audit_stream = RedisAuditStream() if settings.ENV == "prod" else MemoryAuditStream()
