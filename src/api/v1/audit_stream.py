import asyncio
import json
from typing import Literal

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from core.audit.stream import audit_stream
from core.security.rbac import presets

router = APIRouter(
    prefix="/audit/stream",
    tags=["Audit Stream"],
    # Если CanViewAudit — это переменная (например, CanViewAudit = Depends(...)),
    # то в список dependencies мы кладем её напрямую.
    dependencies=[presets.CanViewAudit]
)

def _match_filters(
    event: dict,
    user_id: str | None,
    status_min: int | None,
    level: str | None,
    method: str | None,
    request_id: str | None,
):
    if user_id and str(event.get("user_id")) != user_id:
        return False
    if request_id and str(event.get("request_id")) != request_id:
        return False
    if status_min is not None and event.get("status_code", 0) < status_min:
        return False
    if level and event.get("level") != level:
        return False
    if method and str(event.get("method", "")).upper() != method.upper():
        return False
    return True

@router.get("/", include_in_schema=False)
async def stream_audit(
    user_id: str | None = Query(None),
    request_id: str | None = Query(None),
    status_min: int | None = Query(None),
    level: Literal["info", "warning", "critical"] | None = Query(None),
    method: str | None = Query(None),
    # Здесь CurrentUser нам не нужен, так как CanViewAudit уже проверяет права на уровне роутера.
    # Если же вам НУЖЕН объект юзера внутри функции, используйте:
    # current_user: CurrentUser = presets.CanViewAudit
):
    async def event_generator():
        subscriber = audit_stream.subscribe()
        try:
            yield "retry: 3000\n\n"

            while True:
                try:
                    event = await asyncio.wait_for(anext(subscriber), timeout=15)
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
                    continue
                except asyncio.TimeoutError:
                    yield {"comment": "keep-alive"}
                except StopAsyncIteration:
                    break
                if not _match_filters(event, user_id, status_min, level, method, request_id):
                    continue

                yield f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"

        except asyncio.CancelledError:
            pass
        finally:
            await subscriber.aclose()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
