import pytest

from tests.factories.user import create_user
from tests.utils.auth import login


@pytest.mark.anyio
async def test_login_success(client, dbsession):
    # Arrange
    user = await create_user(dbsession, "admin", "admin123")

    # Act
    data, access_cookie = await login(client, user.login, "admin123")

    # Assert
    assert data["access_token"]
    assert data["refresh_token"]
    assert access_cookie is not None


@pytest.mark.anyio
async def test_login_invalid_password(client, dbsession):
    # Arrange
    user = await create_user(dbsession, "admin", "correct")

    # Act
    response = await client.post(
        "/auth/login",
        data={"username": user.login, "password": "wrong"},
    )

    # Assert
    assert response.status_code == 401
