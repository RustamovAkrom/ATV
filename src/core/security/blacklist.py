# src/core/security/blacklist.py

from datetime import datetime, timezone
from typing import Optional
import time

from core.config import get_settings

settings = get_settings()


# =========================
# MEMORY FALLBACK (DEV)
# =========================

_memory_blacklist: dict[str, float] = {}


class MemoryBlacklist:
    async def add(self, jti: str, exp: datetime):
        _memory_blacklist[jti] = exp.timestamp()

    async def contains(self, jti: str) -> bool:
        now = time.time()

        exp = _memory_blacklist.get(jti)
        if not exp:
            return False

        if exp < now:
            _memory_blacklist.pop(jti, None)
            return False

        return True


# =========================
# REDIS (PROD)
# =========================

class RedisBlacklist:
    def __init__(self, redis):
        self.redis = redis

    async def add(self, jti: str, exp: datetime):
        ttl = int(exp.timestamp() - time.time())
        if ttl <= 0:
            return

        await self.redis.set(f"bl:{jti}", "1", ex=ttl)

    async def contains(self, jti: str) -> bool:
        return await self.redis.exists(f"bl:{jti}") == 1


# =========================
# FACTORY
# =========================

def get_blacklist():
    if settings.USE_REDIS:
        from core.redis import redis_client
        return RedisBlacklist(redis_client)

    return MemoryBlacklist()
