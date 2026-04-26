import pytest

from api.v1.audit import audit_stream as module

pytestmark = pytest.mark.anyio


def test_match_filters_happy_path():
    event = {
        "user_id": "u1",
        "request_id": "r1",
        "status_code": 500,
        "level": "critical",
        "method": "POST",
    }

    assert (
        module._match_filters(
            event,
            user_id="u1",
            status_min=400,
            level="critical",
            method="post",
            request_id="r1",
        )
        is True
    )


@pytest.mark.parametrize(
    ("kwargs", "event"),
    [
        (
            {
                "user_id": "u2",
                "status_min": None,
                "level": None,
                "method": None,
                "request_id": None,
            },
            {"user_id": "u1"},
        ),
        (
            {
                "user_id": None,
                "status_min": 400,
                "level": None,
                "method": None,
                "request_id": None,
            },
            {"status_code": 200},
        ),
        (
            {
                "user_id": None,
                "status_min": None,
                "level": "warning",
                "method": None,
                "request_id": None,
            },
            {"level": "info"},
        ),
        (
            {
                "user_id": None,
                "status_min": None,
                "level": None,
                "method": "POST",
                "request_id": None,
            },
            {"method": "GET"},
        ),
        (
            {
                "user_id": None,
                "status_min": None,
                "level": None,
                "method": None,
                "request_id": "r2",
            },
            {"request_id": "r1"},
        ),
    ],
)
def test_match_filters_rejects_mismatches(kwargs, event):
    assert module._match_filters(event, **kwargs) is False



async def test_stream_audit_emits_retry_and_event(monkeypatch):
    closed = {"value": False}

    from starlette.requests import Request

    async def empty_receive():
        return {"type": "http.request"}
    def make_request():
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
        }
        return Request(scope, receive=empty_receive)


    async def _subscriber():
        try:
            yield {
                "user_id": "u1",
                "request_id": "r1",
                "status_code": 500,
                "level": "critical",
                "method": "POST",
            }
        finally:
            closed["value"] = True

    monkeypatch.setattr(module.audit_stream, "subscribe", lambda: _subscriber())

    response = await module.stream_audit(
        request=make_request(),
        user_id="u1",
        request_id="r1",
        status_min=400,
        level="critical",
        method="POST",
    )
    iterator = response.body_iterator

    first = await anext(iterator)
    second = await anext(iterator)
    await iterator.aclose()

    assert response.media_type == "text/event-stream"
    assert response.headers["Cache-Control"] == "no-cache, no-transform"
    assert first == "retry: 3000\n\n"
    assert second.startswith("data: ")
    assert '"status_code": 500' in second
    assert closed["value"] is True
