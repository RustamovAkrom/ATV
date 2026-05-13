from datetime import UTC, datetime
from uuid import uuid4

import pytest

pytestmark = pytest.mark.anyio


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def stub_expense_service(monkeypatch):
    from api.v1 import expenses as module

    created = {
        "id": str(uuid4()),
        "amount": 1500.5,
        "currency": "UZS",
        "expense_type_code": "repair",
        "description": "Screen replacement",
        "file_url": None,
        "asset": None,
        "repair_id": None,
        "region": None,
        "service": None,
        "created_by": {"id": str(uuid4()), "name": "Admin", "login": "admin"},
        "occurred_at": datetime.now(UTC).isoformat(),
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }

    class _StubExpenseService:
        def __init__(self, _db):
            pass

        async def create_expense(self, data, user_id):
            return created

        async def list_expenses(self, **kwargs):
            return {"total": 1, "page": 1, "size": 20, "items": [created]}

        async def get_expense(self, expense_id):
            return created

        async def update_expense(self, expense_id, data):
            return {**created, "description": "Updated description"}

        async def delete_expense(self, expense_id):
            return None

    monkeypatch.setattr(module, "ExpenseService", _StubExpenseService)


class TestExpenseEndpoints:
    async def test_create_expense_success(self, client, analytics_tokens, stub_expense_service):
        response = await client.post(
            "/expenses/",
            headers=_auth(analytics_tokens["superadmin"]),
            json={
                "amount": 1500.50,
                "currency": "UZS",
                "expense_type": "repair",
                "description": "Screen replacement",
            },
        )
        assert response.status_code == 201
        assert response.json()["amount"] == 1500.5

    async def test_create_expense_negative_amount(self, client, analytics_tokens, stub_expense_service):
        response = await client.post(
            "/expenses/",
            headers=_auth(analytics_tokens["superadmin"]),
            json={"amount": -100, "currency": "UZS", "expense_type": "other"},
        )
        assert response.status_code == 400

    async def test_list_expenses(self, client, analytics_tokens, stub_expense_service):
        response = await client.get(
            "/expenses/",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200
        assert "items" in response.json()

    async def test_get_expense_by_id(self, client, analytics_tokens, stub_expense_service):
        response = await client.get(
            f"/expenses/{uuid4()}",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200

    async def test_update_expense(self, client, analytics_tokens, stub_expense_service):
        response = await client.patch(
            f"/expenses/{uuid4()}",
            headers=_auth(analytics_tokens["superadmin"]),
            json={"description": "Updated description"},
        )
        assert response.status_code == 200

    async def test_delete_expense(self, client, analytics_tokens, stub_expense_service):
        response = await client.delete(
            f"/expenses/{uuid4()}",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"
