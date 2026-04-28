from typing import Callable, Awaitable, Any
from utils.helpers import utc_now
from core.audit.stream import audit_stream


class BaseEventService:
    """
    Executes side-effects in controlled pipeline.
    """

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
        if audit_event:
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
            return

    async def _safe_notify(self, fn):
        try:
            await fn()
        except Exception:
            return
