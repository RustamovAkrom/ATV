import pytest

from db.models.users.user import User
from db.models.users.permission import Role
from db.models.enums import UserRole, UserStatus
from core.security.passwords import hash_password


@pytest.mark.anyio
async def test_login_success(client, dbsession):
    role = Role(name="SuperAdmin", code=UserRole.SUPERADMIN.value)
    dbsession.add(role)
    await dbsession.flush()

    user = User(
        login="admin",
        password_hash=hash_password("admin123"),
        email="admin@test.com",
        phone="+998900000001",
        role_id=role.id,
        status=UserStatus.ACTIVE.value,
    )
    dbsession.add(user)
    await dbsession.commit()

    response = await client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]

    assert "access_token" in response.cookies


@pytest.mark.anyio
async def test_login_invalid_password(client, dbsession):
    role = Role(name="SuperAdmin", code=UserRole.SUPERADMIN.value)
    dbsession.add(role)
    await dbsession.flush()

    user = User(
        login="admin",
        password_hash=hash_password("correct"),
        email="admin@test.com",
        phone="+998900000002",
        role_id=role.id,
        status=UserStatus.ACTIVE.value,
    )
    dbsession.add(user)
    await dbsession.commit()

    response = await client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrong"},
    )

    assert response.status_code == 401
