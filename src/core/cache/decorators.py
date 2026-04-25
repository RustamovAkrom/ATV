import asyncio
from functools import wraps
from typing import Callable

from core.cache.manager import cache


def _tags_tuple(tags: tuple[str, ...] | str | None) -> tuple[str, ...] | None:
    if tags is None:
        return None
    if isinstance(tags, str):
        return (tags,)
    return tuple(str(tag) for tag in tags)


def cached(
    ttl: int = 60,
    tags: tuple[str, ...] | str | None = None,
    lock_ttl: int = 5,
    wait_timeout: float = 0.25,
    wait_interval: float = 0.05,
):
    """
    Endpoint cache decorator.

    - ttl: how long the cached response is kept
    - tags: shared invalidation namespace; optional
    - lock_ttl: short single-flight lock TTL to avoid thundering herd
    - wait_timeout: how long to wait for another request to fill cache
    - wait_interval: polling interval while waiting for cache fill
    """
    resolved_tags = _tags_tuple(tags)

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = await cache.build_key(func, args, kwargs, tags=resolved_tags)
            loop = asyncio.get_running_loop()

            cached_data = await cache.get(key)
            if cached_data is not None:
                return cached_data

            lock_key = f"{key}:lock"
            acquired = await cache.acquire_lock(lock_key, ttl=lock_ttl)

            if not acquired:
                deadline = loop.time() + wait_timeout
                while loop.time() < deadline:
                    cached_data = await cache.get(key)
                    if cached_data is not None:
                        return cached_data
                    await asyncio.sleep(wait_interval)

                # fallback: compute without caching to keep API responsive
                return await func(*args, **kwargs)

            try:
                cached_data = await cache.get(key)
                if cached_data is not None:
                    return cached_data

                result = await func(*args, **kwargs)
                await cache.set(key, result, ttl)
                return result
            finally:
                await cache.release_lock(lock_key)

        return wrapper

    return decorator


def invalidate_cache(tags: tuple[str, ...] | str | None = None):
    resolved_tags = _tags_tuple(tags)

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            await cache.bump_version(resolved_tags or (f"{func.__module__}:{func.__qualname__}",))
            return result

        return wrapper

    return decorator
