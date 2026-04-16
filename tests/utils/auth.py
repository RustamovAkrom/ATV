from httpx import AsyncClient


async def login(client: AsyncClient, login: str, password: str):
    response = await client.post(
        "/auth/login",
        data={"username": login, "password": password},
    )
    assert response.status_code == 200

    data = response.json()
    return data, response.cookies.get("access_token")


def auth_client(client: AsyncClient, access_token: str):
    client.cookies.set("access_token", access_token)
    return client
