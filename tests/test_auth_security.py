from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import update

from core.security.jwt import decode_token
from db.models.refresh_token import RefreshToken


async def login_user(
    client,
    username: str,
    password: str = "password",
    *,
    user_agent: str | None = None,
):
    headers = {"user-agent": user_agent} if user_agent else None

    response = await client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers=headers,
    )

    assert response.status_code == 200, response.text
    return response


@pytest.mark.anyio
async def test_refresh_token_reuse_attack(client, create_user):
    user = await create_user()

    headers = {"user-agent": "test-device"}

    login = await client.post(
        "/auth/login",
        data={"username": user.login, "password": "password"},
        headers=headers,
    )
    assert login.status_code == 200, login.text

    tokens = login.json()
    old_refresh = tokens["refresh_token"]

    # first refresh (OK)
    r1 = await client.post(
        "/auth/refresh",
        json={"refresh_token": old_refresh},
        headers=headers,
    )
    assert r1.status_code == 200, r1.text

    # second reuse (MUST FAIL)
    r2 = await client.post(
        "/auth/refresh",
        json={"refresh_token": old_refresh},
        headers=headers,
    )
    assert r2.status_code == 401


@pytest.mark.anyio
async def test_logout_blacklists_access_token(client, create_user):
    user = await create_user()

    login = await login_user(client, user.login, "password")

    access = login.cookies.get("access_token")
    refresh = login.json()["refresh_token"]

    assert access is not None

    client.cookies.set("access_token", access)

    # logout
    logout_response = await client.post(
        "/auth/logout",
        json={"refresh_token": refresh},
    )
    assert logout_response.status_code == 200, logout_response.text

    # re-set the same access token to verify blacklist, not "missing cookie"
    client.cookies.set("access_token", access)

    response = await client.get("/sessions/")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_logout_all_revokes_all_sessions(client, create_user):
    user = await create_user()

    tokens = []
    access_tokens = []

    for _ in range(2):
        r = await login_user(client, user.login, "password")
        tokens.append(r.json())
        access_tokens.append(r.cookies.get("access_token"))

    assert access_tokens[0] is not None
    assert access_tokens[1] is not None

    client.cookies.set("access_token", access_tokens[1])

    # logout all
    logout_all_response = await client.post("/auth/logout-all")
    assert logout_all_response.status_code == 200, logout_all_response.text

    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens[0]["refresh_token"]},
    )
    assert r.status_code == 401

    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens[1]["refresh_token"]},
    )
    assert r.status_code == 401


@pytest.mark.anyio
async def test_access_token_cannot_be_used_as_refresh(client, create_user):
    user = await create_user()

    login = await login_user(client, user.login, "password")
    access = login.json()["access_token"]

    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": access},
    )
    assert r.status_code == 401


@pytest.mark.anyio
async def test_expired_refresh_token(client, create_user, dbsession):
    user = await create_user()

    login = await login_user(client, user.login, "password")
    refresh = login.json()["refresh_token"]

    # manually expire in DB
    await dbsession.execute(
        update(RefreshToken).values(expires_at=datetime.now(UTC) - timedelta(days=1))
    )
    await dbsession.commit()

    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert r.status_code == 401


@pytest.mark.anyio
async def test_revoke_single_session(client, create_user):
    user = await create_user()

    # login 1
    r1 = await login_user(client, user.login, "password")
    t1 = r1.json()
    access1 = r1.cookies.get("access_token")
    assert access1 is not None

    # login 2
    r2 = await login_user(client, user.login, "password")
    t2 = r2.json()

    payload1 = await decode_token(t1["refresh_token"], "refresh")
    session_id = payload1.jti

    client.cookies.set("access_token", access1)

    sessions_resp = await client.get("/sessions/")
    assert sessions_resp.status_code == 200, sessions_resp.text

    sessions = sessions_resp.json()
    assert any(s["id"] == str(session_id) for s in sessions)

    # revoke ONE session
    revoke_resp = await client.delete(f"/sessions/{session_id}")
    assert revoke_resp.status_code == 200, revoke_resp.text

    # refresh → should fail because revoked session triggers security response
    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": t1["refresh_token"]},
    )
    assert r.status_code == 401

    # second session should also be invalidated by the security policy
    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": t2["refresh_token"]},
    )
    assert r.status_code == 401


@pytest.mark.anyio
async def test_refresh_same_device_ok(client, create_user):
    user = await create_user()

    headers = {"user-agent": "device-1"}

    login = await client.post(
        "/auth/login",
        data={"username": user.login, "password": "password"},
        headers=headers,
    )
    assert login.status_code == 200, login.text

    tokens = login.json()

    refresh = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
        headers=headers,
    )

    assert refresh.status_code == 200, refresh.text


@pytest.mark.anyio
async def test_refresh_different_device_invalid(client, create_user):
    user = await create_user()

    login = await client.post(
        "/auth/login",
        data={"username": user.login, "password": "password"},
        headers={"user-agent": "device-1"},
    )
    assert login.status_code == 200, login.text

    tokens = login.json()

    # different device
    refresh = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
        headers={"user-agent": "device-2"},
    )

    assert refresh.status_code == 401
