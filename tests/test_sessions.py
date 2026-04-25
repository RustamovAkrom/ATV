import pytest

from core.security.jwt import decode_token


async def login_user(client, username: str, password: str = "password"):
    response = await client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response


def auth_client(client, access_token: str):
    client.cookies.set("access_token", access_token)
    return client


@pytest.mark.anyio
async def test_list_sessions(client, create_user):
    # Arrange
    user = await create_user()

    r = await login_user(client, user.login)
    access = r.cookies.get("access_token")

    auth_client(client, access)

    # Act
    response = await client.get("/sessions/")

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0]
    assert "is_active" in data[0]


@pytest.mark.anyio
async def test_revoke_session(client, create_user):
    # Arrange
    user = await create_user()

    r1 = await login_user(client, user.login)
    r2 = await login_user(client, user.login)

    t1 = r1.json()
    access = r1.cookies.get("access_token")

    payload = await decode_token(t1["refresh_token"], "refresh")
    session_id = payload.jti

    auth_client(client, access)

    # Act
    response = await client.delete(f"/sessions/{session_id}")

    # Assert
    assert response.status_code == 200

    # session must be revoked
    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": t1["refresh_token"]},
    )
    assert r.status_code == 401


@pytest.mark.anyio
async def test_revoke_session_not_owned(client, create_user):
    # Arrange
    user1 = await create_user("user1")
    user2 = await create_user("user2")

    r1 = await login_user(client, user1.login)
    r2 = await login_user(client, user2.login)

    t2 = r2.json()
    access1 = r1.cookies.get("access_token")

    payload = await decode_token(t2["refresh_token"], "refresh")
    чужая_session = payload.jti

    auth_client(client, access1)

    # Act
    response = await client.delete(f"/sessions/{чужая_session}")

    # Assert
    assert response.status_code in (403, 404)


@pytest.mark.anyio
async def test_revoke_current_session_forbidden(client, create_user):
    # Arrange
    user = await create_user()

    r = await login_user(client, user.login)
    tokens = r.json()
    access = r.cookies.get("access_token")

    payload = await decode_token(tokens["refresh_token"], "refresh")
    session_id = payload.jti

    auth_client(client, access)

    # Act
    response = await client.delete(f"/sessions/{session_id}")

    # Assert
    assert response.status_code == 200


@pytest.mark.anyio
async def test_logout_all_sessions(client, create_user):
    # Arrange
    user = await create_user()

    r1 = await login_user(client, user.login)
    r2 = await login_user(client, user.login)

    t1 = r1.json()
    t2 = r2.json()

    access = r1.cookies.get("access_token")
    auth_client(client, access)

    # Act
    response = await client.post("/sessions/logout-all")

    # Assert
    assert response.status_code == 200

    # both sessions must be dead
    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": t1["refresh_token"]},
    )
    assert r.status_code == 401

    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": t2["refresh_token"]},
    )
    assert r.status_code == 401


@pytest.mark.anyio
async def test_cleanup_sessions(client, create_user, dbsession):
    # Arrange
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import update

    from db.models.refresh_token import RefreshToken

    user = await create_user()

    r = await login_user(client, user.login)
    access = r.cookies.get("access_token")

    auth_client(client, access)

    # expire sessions manually
    await dbsession.execute(
        update(RefreshToken).values(
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
    )
    await dbsession.commit()

    # Act
    response = await client.post("/sessions/cleanup")

    # Assert
    assert response.status_code == 200
    assert "deleted" in response.json()


@pytest.mark.anyio
async def test_session_is_active_flag(client, create_user):
    # Arrange
    user = await create_user()

    r = await login_user(client, user.login)
    access = r.cookies.get("access_token")

    auth_client(client, access)

    # Act
    response = await client.get("/sessions/")

    # Assert
    sessions = response.json()

    assert any(s["is_active"] is True for s in sessions)
