from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from core.exceptions.errors import NotFound
from schemas.expenses import ExpenseCreateSchema, ExpenseUpdateSchema
from services.expense_service import ExpenseService

pytestmark = pytest.mark.anyio


class _FakeSession:
    def __init__(self):
        self.commits = 0

    async def commit(self):
        self.commits += 1


def _expense_obj(expense_id, amount, expense_type, description):
    now = datetime.now(UTC)
    return SimpleNamespace(
        id=expense_id,
        amount=float(amount),
        currency="UZS",
        expense_type_code=expense_type,
        description=description,
        file_url=None,
        asset=None,
        repair_id=None,
        region=None,
        service=None,
        created_by=SimpleNamespace(id=uuid4(), name="Admin", login="admin"),
        occurred_at=now,
        created_at=now,
        updated_at=now,
    )


class _FakeRepo:
    def __init__(self, session):
        self.session = session
        self.expenses = {}

    async def create_expense(self, data, user_id):
        expense_id = uuid4()
        expense = _expense_obj(
            expense_id,
            data.amount,
            str(data.expense_type),
            data.description,
        )
        self.expenses[expense_id] = expense
        return expense

    async def list_expenses(self, **kwargs):
        return list(self.expenses.values()), len(self.expenses)

    async def get_by_id(self, expense_id):
        return self.expenses.get(expense_id)

    async def update_expense(self, expense_id, data):
        expense = self.expenses.get(expense_id)
        if not expense:
            raise ValueError("not found")
        if data.description is not None:
            expense.description = data.description
        return expense

    async def delete_expense(self, expense_id):
        self.expenses.pop(expense_id, None)

    async def get_by_asset(self, asset_id):
        return [next(iter(self.expenses.values()))] if self.expenses else []

    async def get_by_repair(self, repair_id):
        return [next(iter(self.expenses.values()))] if self.expenses else []

    async def get_by_region(self, region_id):
        return [next(iter(self.expenses.values()))] if self.expenses else []

    async def get_total_amount(self):
        return 1500.0

    async def count(self):
        return 3

    async def get_total_by_type(self):
        return {"repair": 1500.0}

    async def get_total_by_region(self):
        return {uuid4(): 700.0}

    async def get_total_by_service(self):
        return {uuid4(): 800.0}


@pytest.fixture
def expense_service(monkeypatch):
    import services.expense_service as module

    session = _FakeSession()

    def _factory(_session):
        return _FakeRepo(session)

    monkeypatch.setattr(module, "ExpenseRepository", _factory)
    return ExpenseService(session)


class TestExpenseService:
    async def test_create_expense_success(self, expense_service):
        payload = ExpenseCreateSchema(
            amount=1000,
            currency="UZS",
            expense_type="purchase",
            description="Purchase",
        )
        result = await expense_service.create_expense(payload, uuid4())
        assert result.amount == 1000

    async def test_get_expense_not_found(self, expense_service):
        with pytest.raises(NotFound):
            await expense_service.get_expense(uuid4())

    async def test_list_expenses_with_pagination(self, expense_service):
        payload = ExpenseCreateSchema(
            amount=200,
            currency="UZS",
            expense_type="other",
            description="Test",
        )
        await expense_service.create_expense(payload, uuid4())
        result = await expense_service.list_expenses(page=1, size=10)
        assert result.total >= 1
        assert len(result.items) <= 10

    async def test_update_and_delete_expense(self, expense_service):
        payload = ExpenseCreateSchema(
            amount=300,
            currency="UZS",
            expense_type="maintenance",
            description="Before",
        )
        created = await expense_service.create_expense(payload, uuid4())

        updated = await expense_service.update_expense(
            created.id,
            ExpenseUpdateSchema(description="After"),
        )
        assert updated.description == "After"

        await expense_service.delete_expense(created.id)
        with pytest.raises(NotFound):
            await expense_service.delete_expense(created.id)

    async def test_get_expense_stats(self, expense_service):
        result = await expense_service.get_statistics()
        assert result.total_amount == 1500.0
        assert result.total_count == 3
        assert "repair" in result.by_type

    async def test_get_by_asset_repair_region(self, expense_service):
        payload = ExpenseCreateSchema(
            amount=150,
            currency="UZS",
            expense_type="repair",
            description="Linked",
        )
        created = await expense_service.create_expense(payload, uuid4())
        by_asset = await expense_service.get_by_asset(uuid4())
        by_repair = await expense_service.get_by_repair(uuid4())
        by_region = await expense_service.get_by_region(uuid4())
        assert len(by_asset) >= 1
        assert len(by_repair) >= 1
        assert len(by_region) >= 1
        assert by_asset[0].id == created.id
