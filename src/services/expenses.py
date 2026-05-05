"""Service for expenses management."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions.errors import NotFound
from db.models.expenses import Expense
from repositories.expenses import ExpenseRepository
from schemas.expenses import (
    ExpenseCreateSchema,
    ExpenseOutSchema,
    ExpensePageSchema,
    ExpenseStatsSchema,
    ExpenseUpdateSchema,
)


class ExpenseService:
    """Service for managing expenses."""

    def __init__(self, session: AsyncSession):
        """Initialize service."""
        self.repository = ExpenseRepository(session)

    async def create_expense(
        self, data: ExpenseCreateSchema, user_id: UUID
    ) -> ExpenseOutSchema:
        """Create a new expense."""
        expense = await self.repository.create_expense(data, user_id)
        await self.repository.session.commit()
        return ExpenseOutSchema.model_validate(expense, from_attributes=True)

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
    ) -> ExpensePageSchema:
        """List expenses with pagination."""
        items, total = await self.repository.list_expenses(
            page=page,
            size=size,
            expense_type=expense_type,
            region_id=region_id,
            service_id=service_id,
            asset_id=asset_id,
            start_date=start_date,
            end_date=end_date,
        )

        return ExpensePageSchema(
            total=total,
            page=page,
            size=size,
            items=[
                ExpenseOutSchema.model_validate(item, from_attributes=True)
                for item in items
            ],
        )

    async def get_expense(self, expense_id: UUID) -> ExpenseOutSchema:
        """Get a single expense by ID."""
        expense = await self.repository.get_by_id(expense_id)
        if not expense:
            raise NotFound(f"Expense {expense_id} not found")
        return ExpenseOutSchema.model_validate(expense, from_attributes=True)

    async def update_expense(
        self, expense_id: UUID, data: ExpenseUpdateSchema
    ) -> ExpenseOutSchema:
        """Update an expense."""
        await self.get_expense(expense_id)  # Check exists
        expense = await self.repository.update_expense(expense_id, data)
        await self.repository.session.commit()
        return ExpenseOutSchema.model_validate(expense, from_attributes=True)

    async def delete_expense(self, expense_id: UUID) -> None:
        """Delete an expense."""
        await self.get_expense(expense_id)  # Check exists
        await self.repository.delete_expense(expense_id)
        await self.repository.session.commit()

    async def get_by_asset(self, asset_id: UUID) -> list[ExpenseOutSchema]:
        """Get all expenses for an asset."""
        expenses = await self.repository.get_by_asset(asset_id)
        return [
            ExpenseOutSchema.model_validate(item, from_attributes=True)
            for item in expenses
        ]

    async def get_by_repair(self, repair_id: UUID) -> list[ExpenseOutSchema]:
        """Get all expenses for a repair."""
        expenses = await self.repository.get_by_repair(repair_id)
        return [
            ExpenseOutSchema.model_validate(item, from_attributes=True)
            for item in expenses
        ]

    async def get_by_region(self, region_id: UUID) -> list[ExpenseOutSchema]:
        """Get all expenses for a region."""
        expenses = await self.repository.get_by_region(region_id)
        return [
            ExpenseOutSchema.model_validate(item, from_attributes=True)
            for item in expenses
        ]

    async def get_statistics(self) -> ExpenseStatsSchema:
        """Get expense statistics."""
        total_amount = await self.repository.get_total_amount()
        total_count = await self.repository.count()
        by_type = await self.repository.get_total_by_type()
        by_region = await self.repository.get_total_by_region()
        by_service = await self.repository.get_total_by_service()

        return ExpenseStatsSchema(
            total_amount=total_amount,
            total_count=total_count,
            by_type=by_type,
            by_region={str(k): v for k, v in by_region.items()},
            by_service={str(k): v for k, v in by_service.items()},
        )
