import pytest
from db.models.users.user import User
from db.models.users.permission import Role
from db.models.enums import UserRole, UserStatus
from core.security.passwords import hash_password


@pytest.fixture
async def create_user(dbsession):
    async def _create():
        role = Role(name="SuperAdmin", code=UserRole.SUPERADMIN.value)
        dbsession.add(role)
        await dbsession.flush()

        user = User(
            login="test_user",
            password_hash=hash_password("password"),
            email="test@test.com",
            phone="+998900000999",
            role_id=role.id,
            status=UserStatus.ACTIVE.value,
        )

        dbsession.add(user)
        await dbsession.commit()
        return user

    return _create


@pytest.mark.anyio
async def test_refresh_token_reuse_attack(client, dbsession, create_user):
    user = await create_user()
    headers = {"user-agent":
        "test-device"}

    login = await client.post(
        "/auth/login",
        data={"username": user.login, "password": "password"},
        headers=headers,
    )

    tokens = login.json()
    old_refresh = tokens["refresh_token"]

    # first refresh (OK)
    r1 = await client.post(
        "/auth/refresh",
        json={"refresh_token": old_refresh},
        headers=headers,
    )
    assert r1.status_code == 200

    # second reuse (MUST FAIL)
    r2 = await client.post(
        "/auth/refresh",
        json={"refresh_token": old_refresh},
    )

    assert r2.status_code == 401


@pytest.mark.anyio
async def test_logout_blacklists_access_token(client, create_user):
    user = await create_user()

    login = await client.post(
        "/auth/login",
        data={"username": user.login, "password": "password"},
    )

    access = login.cookies.get("access_token")
    refresh = login.json()["refresh_token"]

    # logout
    await client.post(
        "/auth/logout",
        json={"refresh_token": refresh},
    )

    # try using old access token
    response = await client.get(
        "/sessions/",
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_logout_all_revokes_all_sessions(client, create_user):
    user = await create_user()

    tokens = []
    for _ in range(2):
        r = await client.post(
            "/auth/login",
            data={"username": user.login, "password": "password"},
        )
        tokens.append(r.json())

    # logout all
    await client.post(
        "/auth/logout-all",
    )

    # refresh must fail
    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens[1]["refresh_token"]},
    )

    assert r.status_code == 401


@pytest.mark.anyio
async def test_access_token_cannot_be_used_as_refresh(client, create_user):
    user = await create_user()

    login = await client.post(
        "/auth/login",
        data={"username": user.login, "password": "password"},
    )

    access = login.json()["access_token"]

    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": access},
    )

    assert r.status_code == 401

@pytest.mark.anyio
async def test_expired_refresh_token(client, create_user, dbsession):
    user = await create_user()

    login = await client.post(
        "/auth/login",
        data={"username": user.login, "password": "password"},
    )

    refresh = login.json()["refresh_token"]

    # manually expire in DB
    from db.models.refresh_token import RefreshToken
    from sqlalchemy import update
    from datetime import datetime, timezone, timedelta

    await dbsession.execute(
        update(RefreshToken)
        .values(expires_at=datetime.now(timezone.utc) - timedelta(days=1))
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
    r1 = await client.post(
        "/auth/login",
        data={"username": user.login, "password": "password"},
    )
    t1 = r1.json()

    # login 2
    r2 = await client.post(
        "/auth/login",
        data={"username": user.login, "password": "password"},
    )
    t2 = r2.json()

    # get sessions
    sessions_resp = await client.get("/sessions/")
    sessions = sessions_resp.json()

    session_to_revoke = next(s["id"] for s in sessions if not s["is_revoked"])

    # revoke ONE session
    await client.delete(f"/sessions/{session_to_revoke}")

    # 🔥 первый refresh → триггерит security event
    r = await client.post(
        "/auth/refresh",
        json={"refresh_token": t1["refresh_token"]},
    )
    assert r.status_code == 401

    # 🔥 второй тоже должен умереть (revoke_all)
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

    tokens = login.json()

    refresh = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
        headers=headers,
    )

    assert refresh.status_code == 200


@pytest.mark.anyio
async def test_refresh_different_device_invalid(client, create_user):
    user = await create_user()

    login = await client.post(
        "/auth/login",
        data={"username": user.login, "password": "password"},
        headers={"user-agent": "device-1"},
    )

    tokens = login.json()

    # другой девайс
    refresh = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
        headers={"user-agent": "device-2"},
    )

    assert refresh.status_code == 401
