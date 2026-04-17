import time
from datetime import datetime

from core.redis import redis_client
from core.config import get_settings

settings = get_settings()

_memory_blacklist: dict[str, float] = {}


class MemoryBlacklist:
    async def add(self, jti: str, exp: datetime):
        _memory_blacklist[str(jti)] = exp.timestamp()

    async def contains(self, jti: str) -> bool:
        now = time.time()
        key = str(jti)

        exp = _memory_blacklist.get(key)
        if exp is None:
            return False

        if exp < now:
            _memory_blacklist.pop(jti, None)
            return False

        return True


class RedisBlacklist:
    def __init__(self, redis):
        self.redis = redis

    async def add(self, jti: str, exp: datetime):
        ttl = int(exp.timestamp() - time.time())
        if ttl <= 0:
            return

        await self.redis.set(f"bl:{str(jti)}", "1", ex=ttl)

    async def contains(self, jti: str) -> bool:
        return bool(await self.redis.exists(f"bl:{str(jti)}"))


_blacklist: MemoryBlacklist | RedisBlacklist | None = None

def get_blacklist():
    global _blacklist

    if _blacklist is not None:
        return _blacklist

    if settings.ENV == "prod":
        _blacklist = RedisBlacklist(redis_client)
    else:
        _blacklist = MemoryBlacklist()

    return _blacklist
