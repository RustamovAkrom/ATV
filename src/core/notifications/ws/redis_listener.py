import asyncio
import json
from uuid import UUID


class RedisListener:
    def __init__(self, redis, memory_backend):
        self.redis = redis
        self.memory = memory_backend

    async def listen_user(self, user_id: UUID):
        pubsub = self.redis.pubsub()
        channel = f"ws:user:{user_id}"

        await pubsub.subscribe(channel)

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            data = json.loads(message["data"])
            await self.memory.publish(user_id, data)
