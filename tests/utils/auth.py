from httpx import AsyncClient


async def login(
    client: AsyncClient,
    login: str,
    password: str,
    *,
    user_agent: str | None = None,
    return_response: bool = False,
):
    headers = {"user-agent": user_agent} if user_agent else None
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": login, "password": password},
        headers=headers,
    )
    assert response.status_code == 200

    if return_response:
        return response

    data = response.json()
    return data, response.cookies.get("access_token")


def auth_client(client: AsyncClient, access_token: str):
    client.cookies.set("access_token", access_token)
    return client
