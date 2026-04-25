import pytest

from db.models.audit.audit_log import AuditLog
from tests.utils.auth import auth_client, login


@pytest.mark.anyio
async def test_list_audit_logs_requires_authentication(client):
    """Неавторизованный пользователь не должен читать audit-логи."""
    response = await client.get("/audit/")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_list_audit_logs_success_as_admin(client, create_user, dbsession):
    """Superadmin должен получать страницу и рабочую фильтрацию."""
    admin = await create_user(login="audit_admin", password="password")
    _, access_token = await login(client, admin.login, "password")
    auth_client(client, access_token)

    dbsession.add_all(
        [
            AuditLog(
                method="POST",
                path="/assets",
                status_code=201,
                user_id=str(admin.id),
                request_id="req-post",
                latency_ms=12,
                ip="127.0.0.1",
                user_agent="pytest",
                query="page=1",
                is_suspicious=False,
            ),
            AuditLog(
                method="GET",
                path="/health",
                status_code=200,
                user_id=str(admin.id),
                request_id="req-get",
                latency_ms=8,
                ip="127.0.0.1",
                user_agent="pytest",
                query=None,
                is_suspicious=False,
            ),
        ]
    )
    await dbsession.commit()

    response = await client.get(
        "/audit/", params={"limit": 10, "page": 1, "method": "POST"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["method"] == "POST"
    assert data["items"][0]["request_id"] == "req-post"


@pytest.mark.anyio
async def test_audit_stats_returns_expected_counters(client, create_user, dbsession):
    """Статистика должна отражать сохраненные audit-записи."""
    admin = await create_user(login="stats_admin", password="password")
    _, access_token = await login(client, admin.login, "password")
    auth_client(client, access_token)

    dbsession.add_all(
        [
            AuditLog(
                method="GET",
                path="/ok",
                status_code=200,
                user_id=str(admin.id),
                request_id="stats-1",
                latency_ms=10,
                ip="127.0.0.1",
                user_agent="pytest",
                query=None,
                is_suspicious=False,
            ),
            AuditLog(
                method="POST",
                path="/client-error",
                status_code=403,
                user_id=str(admin.id),
                request_id="stats-2",
                latency_ms=20,
                ip="127.0.0.1",
                user_agent="pytest",
                query=None,
                is_suspicious=True,
            ),
            AuditLog(
                method="DELETE",
                path="/server-error",
                status_code=503,
                user_id=str(admin.id),
                request_id="stats-3",
                latency_ms=30,
                ip="127.0.0.1",
                user_agent="pytest",
                query=None,
                is_suspicious=False,
            ),
        ]
    )
    await dbsession.commit()

    response = await client.get("/audit/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats == {
        "total": 3,
        "errors": 2,
        "server_errors": 1,
        "suspicious": 1,
    }


# @pytest.mark.anyio
# async def test_audit_stream_filters_events(client, create_user):
#     """SSE-стрим должен отдавать только события, подходящие под фильтр."""
#     admin = await create_user(login="stream_admin", password="password")
#     _, access_token = await login(client, admin.login, "password")
#     auth_client(client, access_token)

#     target_event = {
#         "user_id": str(uuid4()),
#         "method": "POST",
#         "path": "/assets",
#         "status_code": 201,
#         "latency_ms": 15,
#         "ip": "127.0.0.1",
#         "user_agent": "pytest",
#         "query": None,
#         "is_suspicious": False,
#         "level": "info",
#         "request_id": "req-123",
#         "timestamp": 1.0,
#     }
#     ignored_event = {
#         **target_event,
#         "method": "GET",
#         "request_id": "req-ignored",
#     }

#     async with client.stream("GET", "/audit/stream/", params={"method": "POST"}) as response:
#         assert response.status_code == 200

#         async def publish_events():
#             from core.audit.stream import audit_stream

#             await asyncio.sleep(0.05)
#             await audit_stream.publish(ignored_event)
#             await audit_stream.publish(target_event)

#         publisher = asyncio.create_task(publish_events())

#         async for line in response.aiter_lines():
#             if line.startswith("data: "):
#                 received_data = json.loads(line.replace("data: ", ""))
#                 assert received_data["method"] == "POST"
#                 assert received_data["request_id"] == "req-123"
#                 break

#         await publisher
