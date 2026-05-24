# core/events/base.py
from typing import Any, Awaitable, Callable
from utils.helpers import utc_now
from core.audit.stream import audit_stream
from core.config import get_settings


class BaseEventService:
    """Executes side-effects in controlled pipeline."""

    def __init__(self):
        self._settings = get_settings()

    async def execute(
        self,
        *,
        history: Callable[[], Awaitable[Any]] | None = None,
        audit_event: str | None = None,
        audit_payload: dict | None = None,
        notification: Callable[[], Awaitable[Any]] | None = None,
    ):
        # 1. HISTORY (critical)
        if history:
            await history()

        # 2. AUDIT (non-critical)
        if audit_event and self._settings.AUDIT_ENABLED:
            await self._safe_audit(audit_event, audit_payload or {})

        # 3. NOTIFICATION (non-critical)
        if notification:
            await self._safe_notify(notification)

    async def _safe_audit(self, event: str, payload: dict):
        try:
            await audit_stream.publish(
                {
                    "event": event,
                    **payload,
                    "timestamp": utc_now().timestamp(),
                }
            )
        except Exception:
            pass  # Audit failure should not break business flow

    async def _safe_notify(self, fn: Callable[[], Awaitable[Any]]):
        try:
            await fn()
        except Exception:
            pass  # Notification failure should not break business flow
