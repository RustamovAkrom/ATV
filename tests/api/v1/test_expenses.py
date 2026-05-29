import pytest

pytestmark = pytest.mark.anyio


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Host": "localhost"}


async def _create_expense(client, token: str) -> dict:
    response = await client.post(
        "/api/v1/expenses/",
        headers=_auth(token),
        json={
            "amount": 1500.50,
            "currency": "UZS",
            "expense_type": "repair",
            "description": "Screen replacement",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


class TestExpenseEndpoints:
    async def test_create_expense_success(self, client, analytics_tokens):
        created = await _create_expense(client, analytics_tokens["superadmin"])
        assert created["amount"] == 1500.5
        assert "created_by_id" in created
        assert "created_by_name" in created

    async def test_create_expense_negative_amount(self, client, analytics_tokens):
        response = await client.post(
            "/api/v1/expenses/",
            headers=_auth(analytics_tokens["superadmin"]),
            json={"amount": -100, "currency": "UZS", "expense_type": "other"},
        )
        assert response.status_code == 400

    async def test_list_expenses(self, client, analytics_tokens):
        await _create_expense(client, analytics_tokens["superadmin"])
        response = await client.get(
            "/api/v1/expenses/",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200
        assert "items" in response.json()
        assert len(response.json()["items"]) >= 1

    async def test_get_expense_by_id(self, client, analytics_tokens):
        created = await _create_expense(client, analytics_tokens["superadmin"])
        response = await client.get(
            f"/api/v1/expenses/{created['id']}",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    async def test_update_expense(self, client, analytics_tokens):
        created = await _create_expense(client, analytics_tokens["superadmin"])
        response = await client.patch(
            f"/api/v1/expenses/{created['id']}",
            headers=_auth(analytics_tokens["superadmin"]),
            json={"description": "Updated description"},
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"

    async def test_delete_expense(self, client, analytics_tokens):
        created = await _create_expense(client, analytics_tokens["superadmin"])
        response = await client.delete(
            f"/api/v1/expenses/{created['id']}",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"

        missing = await client.get(
            f"/api/v1/expenses/{created['id']}",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        # Deleted expense must not be retrievable anymore.
        assert missing.status_code == 404
