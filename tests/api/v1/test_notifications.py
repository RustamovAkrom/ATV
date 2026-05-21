from datetime import UTC, datetime
from uuid import uuid4

import pytest

from api.dependencies.notifications.notification import get_notification_service

pytestmark = pytest.mark.anyio


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class _StubNotificationService:
    async def list_by_user(self, user_id, is_read, pagination):
        return [
            {
                "id": uuid4(),
                "type": "analytics.alert",
                "title": "Alert",
                "message": "Message",
                "data": {},
                "is_read": False,
                "created_at": datetime.now(UTC),
                "read_at": None,
            }
        ]

    async def mark_as_read(self, notification_id, actor_id):
        return None

    async def mark_all_as_read(self, actor_id):
        return None

    async def get_unread_count(self, actor_id):
        return 3


@pytest.fixture
def override_notification_service(fastapi_app):
    fastapi_app.dependency_overrides[get_notification_service] = lambda: _StubNotificationService()
    yield
    fastapi_app.dependency_overrides.pop(get_notification_service, None)


class TestNotificationEndpoints:
    async def test_list_notifications(self, client, analytics_tokens, override_notification_service):
        response = await client.get(
            "/notifications/",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) == 1

    async def test_mark_as_read(self, client, analytics_tokens, override_notification_service):
        response = await client.post(
            f"/notifications/{uuid4()}/read",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200

    async def test_mark_all_read(self, client, analytics_tokens, override_notification_service):
        response = await client.post(
            "/notifications/read-all",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200

    async def test_get_unread_count(self, client, analytics_tokens, override_notification_service):
        response = await client.get(
            "/notifications/unread-count",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200
        assert response.json()["count"] == 3
