from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from middlewares import audit as module

pytestmark = pytest.mark.anyio


def test_get_level_boundaries():
    assert module._get_level(200) == "info"
    assert module._get_level(404) == "warning"
    assert module._get_level(500) == "critical"


async def test_audit_middleware_passes_through_non_http_scope():
    app = AsyncMock()
    middleware = module.AuditMiddleware(app)

    scope = {"type": "websocket"}
    await middleware(scope, AsyncMock(), AsyncMock())

    app.assert_awaited_once()


async def test_audit_middleware_prod_enqueues_task(monkeypatch):
    sent = []

    async def app(_scope, _receive, send):
        await send({"type": "http.response.start", "status": 201})
        await send({"type": "http.response.body", "body": b"ok", "more_body": False})

    scope = {
        "type": "http",
        "method": "post",
        "path": "/api/v1/assets",
        "query_string": b"q=1",
        "headers": [(b"user-agent", b"pytest-agent"), (b"x-forwarded-for", b"1.2.3.4")],
        "client": ("9.9.9.9", 1234),
        "state": {"user_id": str(uuid4())},
    }

    monkeypatch.setattr(
        module, "get_settings", lambda: SimpleNamespace(ENV="prod", AUDIT_ENABLED=True)
    )
    delay = Mock()
    monkeypatch.setattr(module.process_audit_log_task, "delay", delay)
    monkeypatch.setattr(module.audit_stream, "publish", AsyncMock())

    def _create_task(coro):
        coro.close()
        return SimpleNamespace(done=lambda: True)

    monkeypatch.setattr(module.asyncio, "create_task", _create_task)

    async def _send(message):
        sent.append(message)

    middleware = module.AuditMiddleware(app)
    await middleware(scope, AsyncMock(), _send)

    assert sent[0]["status"] == 201
    delay.assert_called_once()
    payload = delay.call_args.args[0]
    assert payload["method"] == "POST"
    assert payload["path"] == "/api/v1/assets"
    assert payload["status_code"] == 201
    assert payload["ip"] == "1.2.3.4"
