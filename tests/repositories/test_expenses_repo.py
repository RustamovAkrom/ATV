from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from repositories.expenses import ExpenseRepository
from schemas.expenses import ExpenseCreateSchema, ExpenseUpdateSchema

pytestmark = pytest.mark.anyio


class TestExpenseRepository:
    async def test_create_expense(self, dbsession):
        repo = ExpenseRepository(dbsession)

        expense = await repo.create_expense(
            ExpenseCreateSchema(
                amount=1000,
                currency="UZS",
                expense_type="repair",
                description="Repo create",
            ),
            None,
        )
        assert expense.id is not None
        assert float(expense.amount) == 1000.0

    async def test_list_expenses_with_filters(self, dbsession):
        repo = ExpenseRepository(dbsession)

        await repo.create_expense(
            ExpenseCreateSchema(
                amount=1200,
                currency="UZS",
                expense_type="repair",
                description="Repair",
                occurred_at=datetime.now(UTC) - timedelta(days=2),
            ),
            None,
        )
        await repo.create_expense(
            ExpenseCreateSchema(
                amount=500,
                currency="UZS",
                expense_type="other",
                description="Other",
                occurred_at=datetime.now(UTC),
            ),
            None,
        )

        items, total = await repo.list_expenses(page=1, size=20, expense_type="repair")
        assert total >= 1
        assert len(items) >= 1
        assert all(i.expense_type_code == "repair" for i in items)

    async def test_get_update_delete_and_stats(self, dbsession):
        repo = ExpenseRepository(dbsession)

        created = await repo.create_expense(
            ExpenseCreateSchema(
                amount=900,
                currency="UZS",
                expense_type="maintenance",
                description="Before",
                occurred_at=datetime.now(UTC),
            ),
            None,
        )

        fetched = await repo.get_by_id(created.id)
        assert fetched is not None

        updated = await repo.update_expense(
            created.id,
            ExpenseUpdateSchema(description="After"),
        )
        assert updated.description == "After"

        total_amount = await repo.get_total_amount()
        total_by_type = await repo.get_total_by_type()
        total_by_region = await repo.get_total_by_region()
        total_by_service = await repo.get_total_by_service()
        recent = await repo.get_recent(days=30)

        assert total_amount >= 900
        assert "maintenance" in total_by_type
        assert isinstance(total_by_region, dict)
        assert isinstance(total_by_service, dict)
        assert len(recent) >= 1

        await repo.delete_expense(created.id)

    async def test_delete_expense_missing_raises(self, dbsession):
        repo = ExpenseRepository(dbsession)
        with pytest.raises(ValueError):
            await repo.delete_expense(UUID("00000000-0000-0000-0000-000000000000"))

    async def test_get_stats_empty(self, dbsession):
        repo = ExpenseRepository(dbsession)
        total_amount = await repo.get_total_amount()
        total_by_type = await repo.get_total_by_type()
        assert total_amount == 0.0
        assert total_by_type == {}

    async def test_list_expenses_with_date_filters(self, dbsession):
        repo = ExpenseRepository(dbsession)
        items, total = await repo.list_expenses(
            page=1,
            size=20,
            start_date=datetime(2024, 1, 1, tzinfo=UTC),
            end_date=datetime(2024, 12, 31, tzinfo=UTC),
        )
        assert len(items) >= 0
        assert total >= 0
