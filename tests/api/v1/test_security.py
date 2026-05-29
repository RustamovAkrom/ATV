import pytest

from tests.utils.auth import auth_client, login

pytestmark = pytest.mark.anyio

# =========================================================
# FORGOT PASSWORD
# =========================================================


@pytest.mark.anyio
async def test_forgot_password_existing_user(client, dbsession, create_user):
    user = await create_user()

    response = await client.post(
        "/api/v1/security/forgot-password",
        json={"login": user.login},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.anyio
async def test_forgot_password_non_existing_user(client):
    response = await client.post(
        "/api/v1/security/forgot-password",
        json={"login": "not_exist"},
    )

    # 🔥 защита от enumeration
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# =========================================================
# RESET PASSWORD
# =========================================================


@pytest.mark.anyio
async def test_reset_password_success(client, dbsession, monkeypatch, create_user):
    monkeypatch.setattr(
        "utils.reset_tokens.generate_token",
        lambda: "test-token",
    )

    user = await create_user(password="oldpass")

    # forgot password
    await client.post(
        "/api/v1/security/forgot-password",
        json={"login": user.login},
    )

    # reset
    r = await client.post(
        "/api/v1/security/reset-password",
        json={
            "token": "test-token",
            "new_password": "Newpass123",
        },
    )

    assert r.status_code == 200

    # старый пароль больше не работает
    r = await client.post(
        "/api/v1/auth/login",
        data={"username": user.login, "password": "oldpass"},
    )
    assert r.status_code == 401

    # новый работает
    r = await client.post(
        "/api/v1/auth/login",
        data={"username": user.login, "password": "Newpass123"},
    )
    assert r.status_code == 200


@pytest.mark.anyio
async def test_reset_password_invalid_token(client):
    response = await client.post(
        "/api/v1/security/reset-password",
        json={
            "token": "invalid",
            "new_password": "Newpass123",
        },
    )

    assert response.status_code == 401


# =========================================================
# TOKEN REUSE ATTACK
# =========================================================


@pytest.mark.anyio
async def test_reset_token_reuse(client, dbsession, monkeypatch, create_user):
    monkeypatch.setattr(
        "utils.reset_tokens.generate_token",
        lambda: "test-token",
    )

    user = await create_user()

    await client.post(
        "/api/v1/security/forgot-password",
        json={"login": user.login},
    )

    # первый reset
    r1 = await client.post(
        "/api/v1/security/reset-password",
        json={"token": "test-token", "new_password": "Newpass123"},
    )
    assert r1.status_code == 200

    # второй reset (reuse)
    r2 = await client.post(
        "/api/v1/security/reset-password",
        json={"token": "test-token", "new_password": "Newpass123"},
    )

    assert r2.status_code == 401


# =========================================================
# PASSWORD CHANGE EFFECT
# =========================================================


@pytest.mark.anyio
async def test_password_changed_after_reset(client, dbsession, monkeypatch, create_user):
    monkeypatch.setattr(
        "utils.reset_tokens.generate_token",
        lambda: "test-token",
    )

    user = await create_user(password="oldpass")

    await client.post(
        "/api/v1/security/forgot-password",
        json={"login": user.login},
    )

    await client.post(
        "/api/v1/security/reset-password",
        json={"token": "test-token", "new_password": "Newpass123"},
    )

    # проверка
    r = await client.post(
        "/api/v1/auth/login",
        data={"username": user.login, "password": "Newpass123"},
    )
    assert r.status_code == 200


# =========================================================
# SESSION REVOKE AFTER RESET
# =========================================================


@pytest.mark.anyio
async def test_sessions_revoked_after_password_reset(
    client,
    dbsession,
    monkeypatch,
    create_user,
):
    # 🔥 подменяем generate_token
    monkeypatch.setattr(
        "utils.reset_tokens.generate_token",
        lambda: "test-token",
    )

    user = await create_user()

    # login
    tokens, access = await login(client, user.login, "password")
    client = auth_client(client, access)

    # request reset
    await client.post(
        "/api/v1/security/forgot-password",
        json={"login": user.login},
    )

    # reset с тем же token
    r = await client.post(
        "/api/v1/security/reset-password",
        json={
            "token": "test-token",
            "new_password": "Newpass123",
        },
    )

    assert r.status_code == 200

    # access должен стать невалидным
    r = await client.get("/api/v1/sessions/")
    assert r.status_code in (401, 403)


# =========================================================
# RATE LIMIT (опционально)
# =========================================================


@pytest.mark.anyio
async def test_forgot_password_rate_limit(client):
    for _ in range(5):
        await client.post(
            "/api/v1/security/forgot-password",
            json={"login": "user"},
        )

    # дальше должен быть 429 (если limiter настроен)
