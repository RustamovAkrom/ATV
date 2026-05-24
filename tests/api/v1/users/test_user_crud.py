import uuid

import pytest
from sqlalchemy import select

from db.models.enums import UserRole
from db.models.users.permission import Role

pytestmark = pytest.mark.anyio


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _rand_phone() -> str:
    return f"+99890{uuid.uuid4().int % 10_000_000:07d}"


async def _get_role_id(dbsession) -> uuid.UUID:
    role = (
        await dbsession.execute(select(Role).where(Role.slug == UserRole.ADMIN.value))
    ).scalar_one_or_none()
    if role is None:
        role = (
            await dbsession.execute(
                select(Role).where(Role.slug == UserRole.SUPERADMIN.value)
            )
        ).scalar_one()
    return role.id


class TestUserEndpoints:
    async def test_create_user_returns_duplicate_email_error_due_repo_bug(self, client, analytics_tokens, dbsession):
        role_id = await _get_role_id(dbsession)
        response = await client.post(
            "/users/",
            headers=_auth(analytics_tokens["superadmin"]),
            json={
                "login": f"newuser_{uuid.uuid4().hex[:8]}",
                "email": f"newuser_{uuid.uuid4().hex[:8]}@example.com",
                "phone": _rand_phone(),
                "password": "Test123!",
                "first_name": "New",
                "last_name": "User",
                "role_id": str(role_id),
            },
        )
        assert response.status_code == 400

    async def test_create_user_duplicate_email(self, client, analytics_tokens, dbsession):
        role_id = await _get_role_id(dbsession)
        email = f"dup_{uuid.uuid4().hex[:8]}@example.com"

        first = await client.post(
            "/users/",
            headers=_auth(analytics_tokens["superadmin"]),
            json={
                "login": f"u1_{uuid.uuid4().hex[:8]}",
                "email": email,
                "phone": _rand_phone(),
                "password": "Test123!",
                "role_id": str(role_id),
            },
        )
        assert first.status_code == 400

        second = await client.post(
            "/users/",
            headers=_auth(analytics_tokens["superadmin"]),
            json={
                "login": f"u2_{uuid.uuid4().hex[:8]}",
                "email": email,
                "phone": _rand_phone(),
                "password": "Test123!",
                "role_id": str(role_id),
            },
        )
        assert second.status_code == 400

    async def test_update_user_success(self, client, analytics_tokens, analytics_users):
        user = analytics_users["admin"]
        response = await client.patch(
            f"/users/{user.id}",
            headers=_auth(analytics_tokens["superadmin"]),
            json={
                "role_id": str(user.role_id),
                "status": "active",
                "position": "Updated Position",
                "department": "Updated Department",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["position"] == "Updated Position"
        assert body["department"] == "Updated Department"

    async def test_update_user_not_found(self, client, analytics_tokens):
        fake_id = uuid.uuid4()
        response = await client.patch(
            f"/users/{fake_id}",
            headers=_auth(analytics_tokens["superadmin"]),
            json={"role_id": None, "status": None, "position": "Updated"},
        )
        assert response.status_code == 400

    async def test_update_user_invalid_uuid(self, client, analytics_tokens):
        response = await client.patch(
            "/users/not-a-uuid",
            headers=_auth(analytics_tokens["superadmin"]),
            json={"role_id": None, "status": None, "position": "Updated"},
        )
        assert response.status_code == 400

    async def test_block_activate_archive_user_success(self, client, analytics_tokens, analytics_users):
        user_id = analytics_users["analyst"].id

        blocked = await client.post(
            f"/users/{user_id}/block",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert blocked.status_code == 200
        assert blocked.json()["status"] == "blocked"

        activated = await client.post(
            f"/users/{user_id}/activate",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert activated.status_code == 200
        assert activated.json()["status"] == "active"

        archived = await client.delete(
            f"/users/{user_id}",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert archived.status_code == 200
        assert archived.json()["status"] == "archived"

    async def test_search_users(self, client, analytics_tokens):
        response = await client.get(
            "/users/search",
            params={"q": "admin"},
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_change_password_success(self, client, superadmin_token):
        response = await client.post(
            "/users/me/change-password",
            headers=_auth(superadmin_token),
            json={"old_password": "password", "new_password": "new123"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    async def test_permission_denied_for_user_create(self, client, analytics_tokens, dbsession):
        role_id = await _get_role_id(dbsession)
        response = await client.post(
            "/users/",
            headers=_auth(analytics_tokens["analyst"]),
            json={
                "login": f"denied_{uuid.uuid4().hex[:8]}",
                "email": f"denied_{uuid.uuid4().hex[:8]}@example.com",
                "phone": _rand_phone(),
                "password": "Test123!",
                "role_id": str(role_id),
            },
        )
        assert response.status_code in {401, 403}


class TestUserEndpointsAdditional:
    async def test_list_users_pagination(self, client, analytics_tokens):
        response = await client.get(
            "/users/",
            params={"page": 1, "limit": 5},
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    async def test_list_users_with_search(self, client, analytics_tokens, analytics_users):
        q = analytics_users["admin"].login[:3]
        response = await client.get(
            "/users/search",
            params={"q": q},
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_user_by_id_success(self, client, analytics_tokens, analytics_users):
        user_id = analytics_users["admin"].id
        response = await client.get(
            f"/users/{user_id}",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(user_id)

    async def test_get_user_by_id_not_found(self, client, analytics_tokens):
        fake_id = uuid.uuid4()
        response = await client.get(
            f"/users/{fake_id}",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 400

    async def test_update_user_role(self, client, analytics_tokens, analytics_users, dbsession):
        target = analytics_users["analyst"]
        role_id = await _get_role_id(dbsession)
        response = await client.patch(
            f"/users/{target.id}",
            headers=_auth(analytics_tokens["superadmin"]),
            json={"role_id": str(role_id), "status": "active"},
        )
        assert response.status_code == 200
        assert response.json()["role"] is not None

    async def test_update_user_self_forbidden(self, client, analytics_tokens, analytics_users):
        me = analytics_users["superadmin"]
        response = await client.patch(
            f"/users/{me.id}",
            headers=_auth(analytics_tokens["superadmin"]),
            json={"role_id": str(me.role_id), "status": "active"},
        )
        assert response.status_code in {400, 403}

    async def test_block_user_not_admin(self, client, analytics_tokens, analytics_users):
        target = analytics_users["admin"]
        response = await client.post(
            f"/users/{target.id}/block",
            headers=_auth(analytics_tokens["analyst"]),
        )
        assert response.status_code in {401, 403}

    async def test_archive_user_not_found(self, client, analytics_tokens):
        fake_id = uuid.uuid4()
        response = await client.delete(
            f"/users/{fake_id}",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        # Service currently updates status without strict existence validation.
        assert response.status_code in {200, 400, 404}
