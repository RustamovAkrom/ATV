"""Repository for expenses operations."""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.expenses import Expense
from repositories.base import BaseRepository
from schemas.expenses import (
    ExpenseCreateSchema,
    ExpenseOutSchema,
    ExpenseUpdateSchema,
)


class ExpenseRepository(BaseRepository):
    """Repository for managing expenses."""

    def __init__(self, session: AsyncSession):
        """Initialize repository."""
        super().__init__(session)

    async def create_expense(
        self, data: ExpenseCreateSchema, created_by_id: UUID
    ) -> Expense:
        """Create new expense."""
        expense = Expense(
            amount=data.amount,
            currency=data.currency,
            expense_type_code=data.expense_type,
            description=data.description,
            asset_id=data.asset_id,
            repair_id=data.repair_id,
            region_id=data.region_id,
            service_id=data.service_id,
            file_url=data.file_url,
            occurred_at=data.occurred_at or datetime.now(),
            created_by=created_by_id,
        )
        self.session.add(expense)
        await self.session.flush()
        return expense

    async def list_expenses(
        self,
        page: int = 1,
        size: int = 20,
        expense_type: str | None = None,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        asset_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[list[Expense], int]:
        """List expenses with filters."""
        query = select(Expense)

        if expense_type:
            query = query.where(Expense.expense_type_code == expense_type)
        if region_id:
            query = query.where(Expense.region_id == region_id)
        if service_id:
            query = query.where(Expense.service_id == service_id)
        if asset_id:
            query = query.where(Expense.asset_id == asset_id)
        if start_date:
            query = query.where(Expense.occurred_at >= start_date)
        if end_date:
            query = query.where(Expense.occurred_at <= end_date)

        # Get total count
        count_query = select(func.count()).select_from(Expense)
        if expense_type:
            count_query = count_query.where(Expense.expense_type_code == expense_type)
        if region_id:
            count_query = count_query.where(Expense.region_id == region_id)
        if service_id:
            count_query = count_query.where(Expense.service_id == service_id)
        if asset_id:
            count_query = count_query.where(Expense.asset_id == asset_id)
        if start_date:
            count_query = count_query.where(Expense.occurred_at >= start_date)
        if end_date:
            count_query = count_query.where(Expense.occurred_at <= end_date)

        total = await self.session.scalar(count_query)

        # Order and paginate
        query = query.order_by(desc(Expense.occurred_at))
        query = query.offset((page - 1) * size).limit(size)

        result = await self.session.execute(query)
        items = result.scalars().all()

        return items, total

    async def get_by_id(self, expense_id: UUID) -> Expense | None:
        """Get a single expense by ID."""
        query = select(Expense).where(Expense.id == expense_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_expense(self, expense_id: UUID) -> None:
        """Delete an expense by ID."""
        expense = await self.get_by_id(expense_id)
        if not expense:
            raise ValueError(f"Expense {expense_id} not found")
        self.session.delete(expense)

    async def get_by_asset(self, asset_id: UUID) -> list[Expense]:
        """Get all expenses for an asset."""
        query = (
            select(Expense)
            .where(Expense.asset_id == asset_id)
            .order_by(desc(Expense.occurred_at))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_repair(self, repair_id: UUID) -> list[Expense]:
        """Get all expenses for a repair."""
        query = (
            select(Expense)
            .where(Expense.repair_id == repair_id)
            .order_by(desc(Expense.occurred_at))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_region(self, region_id: UUID) -> list[Expense]:
        """Get all expenses for a region."""
        query = (
            select(Expense)
            .where(Expense.region_id == region_id)
            .order_by(desc(Expense.occurred_at))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_total_by_type(self) -> dict[str, float]:
        """Get total amount by expense type."""
        query = select(
            Expense.expense_type_code, func.sum(Expense.amount).label("total")
        ).group_by(Expense.expense_type_code)
        result = await self.session.execute(query)
        return {row[0]: float(row[1]) for row in result.all()}

    async def get_total_by_region(self) -> dict[UUID, float]:
        """Get total amount by region."""
        query = (
            select(Expense.region_id, func.sum(Expense.amount).label("total"))
            .where(Expense.region_id.isnot(None))
            .group_by(Expense.region_id)
        )
        result = await self.session.execute(query)
        return {row[0]: float(row[1]) for row in result.all()}

    async def get_total_by_service(self) -> dict[UUID, float]:
        """Get total amount by service."""
        query = (
            select(Expense.service_id, func.sum(Expense.amount).label("total"))
            .where(Expense.service_id.isnot(None))
            .group_by(Expense.service_id)
        )
        result = await self.session.execute(query)
        return {row[0]: float(row[1]) for row in result.all()}

    async def get_total_amount(self) -> float:
        """Get total amount of all expenses."""
        query = select(func.sum(Expense.amount))
        result = await self.session.scalar(query)
        return float(result or 0)

    async def get_recent(self, days: int = 30) -> list[Expense]:
        """Get expenses from last N days."""
        start_date = datetime.now() - timedelta(days=days)
        query = (
            select(Expense)
            .where(Expense.occurred_at >= start_date)
            .order_by(desc(Expense.occurred_at))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_expense(
        self, expense_id: UUID, data: ExpenseUpdateSchema
    ) -> Expense:
        """Update an expense."""
        expense = await self.get_by_id(expense_id)
        if not expense:
            raise ValueError(f"Expense {expense_id} not found")

        if data.amount is not None:
            expense.amount = data.amount
        if data.currency is not None:
            expense.currency = data.currency
        if data.expense_type is not None:
            expense.expense_type_code = data.expense_type
        if data.description is not None:
            expense.description = data.description
        if data.file_url is not None:
            expense.file_url = data.file_url

        expense.updated_at = datetime.now()
        await self.session.flush()
        return expense
