# core/security/blacklist.py

from datetime import datetime, timezone

from core.redis import redis_client


PREFIX = "blacklist"


async def add_to_blacklist(jti: str, exp: datetime):
    """
    Add token to blacklist with TTL
    """

    now = datetime.now(timezone.utc)
    ttl = int((exp - now).total_seconds())

    if ttl <= 0:
        return

    key = f"{PREFIX}:{jti}"

    await redis_client.set(key, "1", ex=ttl)


async def is_blacklisted(jti: str) -> bool:
    key = f"{PREFIX}:{jti}"
    return await redis_client.exists(key) == 1
