# tests/services/test_expense_service.py
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from core.exceptions.errors import NotFound, PermissionDenied
from schemas.assets.expenses import ExpenseCreateSchema, ExpenseUpdateSchema
from schemas.auth.auth import CurrentUserSchema
from services.assets.expense_service import ExpenseService

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
        region_id=None,
        service=None,
        service_id=None,
        created_by=SimpleNamespace(id=uuid4(), name="Admin", login="admin"),
        occurred_at=now,
        created_at=now,
        updated_at=now,
    )


class _FakeRepo:
    def __init__(self, session):
        self.session = session
        self.expenses = {}
        self._next_id = 0

    async def create(self, data, user_id):
        expense_id = uuid4()
        expense = _expense_obj(
            expense_id,
            data.amount,
            str(data.expense_type),
            data.description,
        )
        self.expenses[expense_id] = expense
        return expense

    async def get(self, expense_id):
        return self.expenses.get(expense_id)

    async def list(
        self,
        page: int = 1,
        limit: int = 20,
        expense_type: str | None = None,
        region_id: str | None = None,
        service_id: str | None = None,
        asset_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ):
        items = list(self.expenses.values())
        total = len(items)

        # Пагинация
        start = (page - 1) * limit
        end = start + limit
        items = items[start:end]

        return items, total

    async def update(self, expense_id, data):
        expense = self.expenses.get(expense_id)
        if not expense:
            return None
        if data.description is not None:
            expense.description = data.description
        return expense

    async def delete(self, expense_id):
        return self.expenses.pop(expense_id, None) is not None

    async def get_asset(self, asset_id):
        return SimpleNamespace(id=asset_id, region_id=None, service_id=None)

    async def get_repair(self, repair_id):
        return SimpleNamespace(asset_id=uuid4())

    async def get_by_asset(self, asset_id):
        return list(self.expenses.values())

    async def get_by_repair(self, repair_id):
        return list(self.expenses.values())

    async def get_by_region(self, region_id):
        return list(self.expenses.values())

    async def get_statistics(self):
        return {
            "total_amount": 1500.0,
            "total_count": 3,
            "by_type": {"repair": 1500.0},
            "by_region": {str(uuid4()): 700.0},
            "by_service": {str(uuid4()): 800.0},
        }


@pytest.fixture
def fake_session():
    return _FakeSession()


@pytest.fixture
def fake_repo(fake_session):
    return _FakeRepo(fake_session)


@pytest.fixture
def mock_actor():
    return CurrentUserSchema(
        id=uuid4(),
        role="superadmin",
        permissions=[],
        assigned_region_id=None,
        assigned_service_id=None,
    )


@pytest.fixture
def expense_service(fake_repo):
    return ExpenseService(fake_repo)


class TestExpenseService:
    async def test_create_expense_success(self, expense_service, mock_actor):
        """Test successful expense creation."""
        payload = ExpenseCreateSchema(
            amount=1000,
            currency="UZS",
            expense_type="purchase",
            description="Purchase",
        )
        result = await expense_service.create(payload, mock_actor)
        assert result.amount == 1000
        assert result.currency == "UZS"
        assert result.description == "Purchase"

    async def test_create_expense_with_asset(self, expense_service, mock_actor):
        """Test expense creation linked to an asset."""
        asset_id = uuid4()
        payload = ExpenseCreateSchema(
            amount=500,
            currency="UZS",
            expense_type="repair",
            description="Asset repair",
            asset_id=asset_id,
        )
        result = await expense_service.create(payload, mock_actor)
        assert result.amount == 500

    async def test_get_expense_success(self, expense_service, mock_actor):
        """Test retrieving an expense by ID."""
        payload = ExpenseCreateSchema(
            amount=100,
            currency="UZS",
            expense_type="other",
            description="Test expense",
        )
        created = await expense_service.create(payload, mock_actor)

        result = await expense_service.get(created.id, mock_actor)
        assert result.id == created.id
        assert result.amount == 100

    async def test_get_expense_not_found(self, expense_service, mock_actor):
        """Test retrieving a non-existent expense."""
        with pytest.raises(NotFound):
            await expense_service.get(uuid4(), mock_actor)

    async def test_list_expenses_with_pagination(self, expense_service, mock_actor):
        """Test listing expenses with pagination."""
        for i in range(3):
            payload = ExpenseCreateSchema(
                amount=100 * (i + 1),
                currency="UZS",
                expense_type="other",
                description=f"Test {i}",
            )
            await expense_service.create(payload, mock_actor)

        result = await expense_service.list(actor=mock_actor, page=1, limit=2)
        assert result.total >= 3
        assert len(result.items) == 2
        assert result.page == 1
        assert result.size == 2

    async def test_update_expense_success(self, expense_service, mock_actor):
        """Test updating an expense."""
        payload = ExpenseCreateSchema(
            amount=300,
            currency="UZS",
            expense_type="maintenance",
            description="Before",
        )
        created = await expense_service.create(payload, mock_actor)

        updated = await expense_service.update(
            created.id,
            ExpenseUpdateSchema(description="After"),
            mock_actor,
        )
        assert updated.description == "After"

    async def test_update_expense_not_found(self, expense_service, mock_actor):
        """Test updating a non-existent expense."""
        with pytest.raises(NotFound):
            await expense_service.update(
                uuid4(),
                ExpenseUpdateSchema(description="New"),
                mock_actor,
            )

    async def test_delete_expense_success(self, expense_service, mock_actor):
        """Test deleting an expense."""
        payload = ExpenseCreateSchema(
            amount=400,
            currency="UZS",
            expense_type="logistics",
            description="To be deleted",
        )
        created = await expense_service.create(payload, mock_actor)

        expense = await expense_service.get(created.id, mock_actor)
        assert expense.id == created.id

        await expense_service.delete(created.id, mock_actor)

        with pytest.raises(NotFound):
            await expense_service.get(created.id, mock_actor)

    async def test_delete_expense_not_found(self, expense_service, mock_actor):
        """Test deleting a non-existent expense."""
        with pytest.raises(NotFound):
            await expense_service.delete(uuid4(), mock_actor)

    async def test_get_expense_stats(self, expense_service):
        """Test getting expense statistics."""
        result = await expense_service.get_statistics()
        assert result.total_amount == 1500.0
        assert result.total_count == 3
        assert "repair" in result.by_type

    async def test_get_by_asset(self, expense_service, mock_actor):
        """Test getting expenses by asset."""
        payload = ExpenseCreateSchema(
            amount=150,
            currency="UZS",
            expense_type="repair",
            description="Asset expense",
        )
        created = await expense_service.create(payload, mock_actor)

        by_asset = await expense_service.get_by_asset(uuid4(), mock_actor)
        assert len(by_asset) >= 1
        assert by_asset[0].id == created.id

    async def test_get_by_repair(self, expense_service, mock_actor):
        """Test getting expenses by repair."""
        payload = ExpenseCreateSchema(
            amount=150,
            currency="UZS",
            expense_type="repair",
            description="Repair expense",
        )
        created = await expense_service.create(payload, mock_actor)

        by_repair = await expense_service.get_by_repair(uuid4(), mock_actor)
        assert len(by_repair) >= 1
        assert by_repair[0].id == created.id

    async def test_get_by_region(self, expense_service, mock_actor):
        """Test getting expenses by region."""
        payload = ExpenseCreateSchema(
            amount=150,
            currency="UZS",
            expense_type="repair",
            description="Region expense",
        )
        created = await expense_service.create(payload, mock_actor)

        by_region = await expense_service.get_by_region(uuid4(), mock_actor)
        assert len(by_region) >= 1
        assert by_region[0].id == created.id

    async def test_expense_access_denied_for_wrong_region(self, expense_service):
        """Test that user without region access cannot view expense."""
        region_id = uuid4()
        payload = ExpenseCreateSchema(
            amount=100,
            currency="UZS",
            expense_type="other",
            description="Region restricted",
            region_id=region_id,
        )

        actor = CurrentUserSchema(
            id=uuid4(),
            role="user",
            permissions=[],
            assigned_region_id=uuid4(),
            assigned_service_id=None,
        )

        with pytest.raises(PermissionDenied, match="Access denied: region mismatch"):
            await expense_service.create(payload, actor)
