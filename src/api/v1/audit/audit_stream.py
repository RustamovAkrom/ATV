import asyncio
import json
from typing import Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse

from core.audit.stream import audit_stream

# CanViewAudit — это уже готовый объект зависимости (variable)
from core.security.rbac.presets import AuditPermissions

router = APIRouter(
    prefix="/audit/stream",
    tags=["Audit Stream"],
    # Если CanViewAudit — это переменная (например, CanViewAudit = Depends(...)),
    # то в список dependencies мы кладем её напрямую.
    dependencies=[Depends(AuditPermissions.CanViewAudit)],
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


@router.get(
    "/", include_in_schema=False, dependencies=[Depends(AuditPermissions.CanViewAudit)]
)
async def stream_audit(
    request: Request,
    user_id: str | None = Query(None),
    request_id: str | None = Query(None),
    status_min: int | None = Query(None),
    level: Literal["info", "warning", "critical"] | None = Query(None),
    method: str | None = Query(None),
    # Здесь CurrentUser нам не нужен, так как CanViewAudit уже проверяет права
    # на уровне роутера.
    # Если же вам НУЖЕН объект юзера внутри функции, используйте:
    # current_user: CurrentUser = presets.CanViewAudit
):
    async def event_generator():
        subscriber = audit_stream.subscribe()

        try:
            yield "retry: 3000\n\n"

            try:
                while True:
                    if await request.is_disconnected():
                        break

                    try:
                        event = await asyncio.wait_for(anext(subscriber), timeout=15)
                    except TimeoutError:
                        yield ": keep-alive\n\n"
                        continue

                    except StopAsyncIteration:
                        # Sbuscriber is die
                        break

                    if not _match_filters(
                        event, user_id, status_min, level, method, request_id
                    ):
                        continue
                    try:
                        payload = json.dumps(
                            jsonable_encoder(event),
                            ensure_ascii=False,
                        )
                        yield f"data: {payload}\n\n"

                    except Exception:
                        yield ": serialization-error\n\n"
            except StopAsyncIteration:
                pass

        except asyncio.CancelledError:
            pass

        finally:
            try:
                await subscriber.aclose()
            except Exception:
                pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
