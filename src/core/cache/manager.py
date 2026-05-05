import hashlib
import inspect
import json
from collections.abc import Callable
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from core.cache.backends import MemoryBackend, RedisBackend
from core.config import get_settings
from core.redis import redis_client

settings = get_settings()

_IGNORED_PARAM_NAMES = {
    "self",
    "request",
    "response",
    "background_tasks",
    "db",
    "session",
    "service",
    "repo",
    "client",
}


class CacheManager:
    def __init__(self):
        self.backend = (
            RedisBackend(redis_client) if settings.ENV == "prod" else MemoryBackend()
        )

    def _scope(self, func: Callable, tags: tuple[str, ...] | None = None) -> str:
        if tags:
            return "|".join(sorted({str(tag) for tag in tags}))
        return f"{func.__module__}:{func.__qualname__}"

    def _normalize(self, value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, (UUID, datetime, date, Enum)):
            return str(value)

        if is_dataclass(value):
            return self._normalize(asdict(value))

        if hasattr(value, "model_dump"):
            try:
                return self._normalize(value.model_dump(mode="json"))
            except TypeError:
                return self._normalize(value.model_dump())

        if isinstance(value, dict):
            return {
                str(k): self._normalize(v)
                for k, v in sorted(value.items(), key=lambda item: str(item[0]))
            }

        if isinstance(value, (list, tuple)):
            return [self._normalize(v) for v in value]

        if isinstance(value, set):
            return sorted(self._normalize(v) for v in value)

        return None

    def _bind_arguments(
        self, func: Callable, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        signature = inspect.signature(func)
        bound = signature.bind_partial(*args, **kwargs)
        bound.apply_defaults()

        payload: dict[str, Any] = {}
        for name, value in bound.arguments.items():
            if name in _IGNORED_PARAM_NAMES:
                continue

            normalized = self._normalize(value)
            if normalized is None:
                continue

            payload[name] = normalized

        return payload

    async def _version_for_tag(self, tag: str) -> int:
        return await self.backend.get_int(f"cache:version:{tag}")

    async def _version_token(self, tags: tuple[str, ...]) -> str:
        versions = [str(await self._version_for_tag(tag)) for tag in tags]
        return "-".join(versions)

    async def build_key(
        self,
        func: Callable,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        tags: tuple[str, ...] | None = None,
    ) -> str:
        scope = self._scope(func, tags)
        normalized = self._bind_arguments(func, args, kwargs)

        payload = {
            "scope": scope,
            "args": normalized,
            "versions": await self._version_token(tags or (scope,)),
        }

        raw = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"cache:{scope}:{digest}:v{payload['versions']}"

    def serialize(self, data: Any) -> str:
        encoded = jsonable_encoder(data)
        return json.dumps(
            encoded, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )

    def deserialize(self, raw: str) -> Any:
        return json.loads(raw)

    async def get(self, key: str) -> Any | None:
        raw = await self.backend.get(key)
        if raw is None:
            return None
        return self.deserialize(raw)

    async def set(self, key: str, value: Any, ttl: int) -> None:
        await self.backend.set(key, self.serialize(value), int(ttl))

    async def delete(self, key: str) -> None:
        await self.backend.delete(key)

    async def bump_version(self, tags: tuple[str, ...] | str | None) -> None:
        if tags is None:
            return

        if isinstance(tags, str):
            tags = (tags,)

        unique_tags = tuple(sorted({str(tag) for tag in tags}))
        for tag in unique_tags:
            await self.backend.incr(f"cache:version:{tag}")

    async def acquire_lock(self, key: str, ttl: int = 5) -> bool:
        return await self.backend.acquire_lock(key, ttl)

    async def release_lock(self, key: str) -> None:
        await self.backend.release_lock(key)


cache = CacheManager()
