import time
from typing import Any, Optional, Protocol

from core.redis import redis_client


class CacheBackend(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, value: str, ttl: int) -> None: ...
    async def delete(self, key: str) -> None: ...
    async def incr(self, key: str) -> None: ...
    async def get_int(self, key: str) -> int: ...
    async def acquire_lock(self, key: str, ttl: int) -> bool: ...
    async def release_lock(self, key: str) -> None: ...


class MemoryBackend:
    def __init__(self):
        self.storage: dict[str, tuple[Any, Optional[float]]] = {}

    async def get(self, key: str) -> str | None:
        data = self.storage.get(key)
        if not data:
            return None

        value, exp = data
        if exp is not None and exp < time.time():
            self.storage.pop(key, None)
            return None

        return value

    async def set(self, key: str, value: str, ttl: int) -> None:
        ttl = int(ttl)
        exp = time.time() + ttl if ttl > 0 else None
        self.storage[key] = (value, exp)

    async def delete(self, key: str) -> None:
        self.storage.pop(key, None)

    async def incr(self, key: str) -> int:
        value, exp = self.storage.get(key, (0, None))
        try:
            current = int(value)
        except (TypeError, ValueError):
            current = 0
        current += 1
        self.storage[key] = (current, exp)
        return current

    async def get_int(self, key: str) -> int:
        data = self.storage.get(key)
        if not data:
            return 1

        value, exp = data
        if exp is not None and exp < time.time():
            self.storage.pop(key, None)
            return 1

        try:
            return int(value)
        except (TypeError, ValueError):
            return 1

    async def acquire_lock(self, key: str, ttl: int) -> bool:
        ttl = int(ttl)
        now = time.time()
        data = self.storage.get(key)
        if data:
            _, exp = data
            if exp is None or exp > now:
                return False
        exp = now + ttl if ttl > 0 else None
        self.storage[key] = ("1", exp)
        return True

    async def release_lock(self, key: str) -> None:
        self.storage.pop(key, None)


class RedisBackend:
    def __init__(self, redis=redis_client):
        self.redis = redis

    async def get(self, key: str) -> str | None:
        data = await self.redis.get(key)
        if data is None:
            return None
        if isinstance(data, bytes):
            return data.decode("utf-8")
        return data

    async def set(self, key: str, value: str, ttl: int) -> None:
        ttl = int(ttl)
        if ttl <= 0:
            await self.redis.set(key, value)
            return
        await self.redis.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def incr(self, key: str) -> int:
        return int(await self.redis.incr(key))

    async def get_int(self, key: str) -> int:
        val = await self.redis.get(key)
        if val is None:
            return 1
        if isinstance(val, bytes):
            val = val.decode("utf-8")
        try:
            return int(val)
        except (TypeError, ValueError):
            return 1

    async def acquire_lock(self, key: str, ttl: int) -> bool:
        ttl = int(ttl)
        if ttl <= 0:
            ttl = 5
        # SET key value NX EX ttl
        result = await self.redis.set(key, "1", ex=ttl, nx=True)
        return bool(result)

    async def release_lock(self, key: str) -> None:
        await self.redis.delete(key)
