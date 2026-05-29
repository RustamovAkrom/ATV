import pytest

from tests.utils.auth import login

pytestmark = pytest.mark.anyio


@pytest.mark.anyio
async def test_login_success(client, create_user):
    # Arrange
    user = await create_user("admin", "admin123")

    # Act
    data, access_cookie = await login(client, user.login, "admin123")

    # Assert
    assert data["access_token"]
    assert data["refresh_token"]
    assert access_cookie is not None


@pytest.mark.anyio
async def test_login_invalid_password(client, create_user):
    # Arrange
    user = await create_user("admin", "correct")

    # Act
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user.login, "password": "wrong"},
    )

    # Assert
    assert response.status_code == 401
