"""Repository for expenses operations."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset import Asset
from db.models.expenses import Expense
from db.models.repairs.repair import Repair
from repositories.base import BaseRepository
from schemas.assets.expenses import ExpenseCreateSchema, ExpenseUpdateSchema


class ExpenseRepository(BaseRepository):
    """Repository for expense data access."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create(
        self, data: ExpenseCreateSchema, created_by_id: UUID | None
    ) -> Expense:
        """Create a new expense record."""
        expense_type_code = (
            data.expense_type.value
            if hasattr(data.expense_type, "value")
            else str(data.expense_type)
        )
        expense = Expense(
            amount=data.amount,
            currency=data.currency,
            expense_type_code=expense_type_code,
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
        await self.flush()
        await self.refresh(expense)
        return expense

    async def create_expense(
        self, data: ExpenseCreateSchema, created_by_id: UUID | None
    ) -> Expense:
        """Backward-compatible alias for creating an expense."""
        return await self.create(data, created_by_id)

    async def get(self, expense_id: UUID) -> Expense | None:
        """Get expense by ID."""
        result = await self.session.execute(
            select(Expense).where(Expense.id == expense_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, expense_id: UUID) -> Expense | None:
        """Backward-compatible alias for fetching expense by ID."""
        return await self.get(expense_id)

    async def get_by_asset(self, asset_id: UUID) -> list[Expense]:
        """Get all expenses for an asset."""
        result = await self.session.execute(
            select(Expense)
            .where(Expense.asset_id == asset_id)
            .order_by(desc(Expense.occurred_at))
        )
        return list(result.scalars().all())

    async def get_by_repair(self, repair_id: UUID) -> list[Expense]:
        """Get all expenses for a repair."""
        result = await self.session.execute(
            select(Expense)
            .where(Expense.repair_id == repair_id)
            .order_by(desc(Expense.occurred_at))
        )
        return list(result.scalars().all())

    async def get_by_region(self, region_id: UUID) -> list[Expense]:
        """Get all expenses for a region."""
        result = await self.session.execute(
            select(Expense)
            .where(Expense.region_id == region_id)
            .order_by(desc(Expense.occurred_at))
        )
        return list(result.scalars().all())

    async def list(
        self,
        page: int = 1,
        limit: int = 20,
        expense_type: str | None = None,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        asset_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[list[Expense], int]:
        """List expenses with pagination and filters."""
        query = select(Expense)

        # Apply filters
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

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        # Pagination
        query = query.order_by(desc(Expense.occurred_at))
        query = query.offset((page - 1) * limit).limit(limit)

        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

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
        """Backward-compatible alias for listing expenses."""
        return await self.list(
            page=page,
            limit=size,
            expense_type=expense_type,
            region_id=region_id,
            service_id=service_id,
            asset_id=asset_id,
            start_date=start_date,
            end_date=end_date,
        )

    async def update(
        self, expense_id: UUID, data: ExpenseUpdateSchema
    ) -> Expense | None:
        """Update an existing expense."""
        expense = await self.get(expense_id)
        if not expense:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "expense_type":
                expense.expense_type_code = value.value
            elif hasattr(expense, key):
                setattr(expense, key, value)

        expense.updated_at = datetime.now()
        await self.flush()
        await self.refresh(expense)
        return expense

    async def update_expense(
        self, expense_id: UUID, data: ExpenseUpdateSchema
    ) -> Expense | None:
        """Backward-compatible alias for updating expense."""
        return await self.update(expense_id, data)

    async def delete(self, expense_id: UUID) -> bool:
        """Delete an expense by ID."""
        expense = await self.get(expense_id)
        if not expense:
            return False
        await self.session.delete(expense)
        await self.flush()
        return True

    async def delete_expense(self, expense_id: UUID) -> None:
        """Backward-compatible delete with ValueError on missing entity."""
        deleted = await self.delete(expense_id)
        if not deleted:
            raise ValueError(f"Expense {expense_id} not found")

    async def get_asset(self, asset_id: UUID) -> Asset | None:
        """Get asset by ID."""
        result = await self.session.execute(select(Asset).where(Asset.id == asset_id))
        return result.scalar_one_or_none()

    async def get_repair(self, repair_id: UUID) -> Repair | None:
        """Get repair by ID."""
        result = await self.session.execute(
            select(Repair).where(Repair.id == repair_id)
        )
        return result.scalar_one_or_none()

    async def get_statistics(self) -> dict:
        """Get expense statistics."""
        # Total amount and count
        total_result = await self.session.execute(
            select(func.sum(Expense.amount), func.count(Expense.id))
        )
        total_amount, total_count = total_result.one()
        total_amount = float(total_amount or 0)
        total_count = total_count or 0

        # By type
        by_type_result = await self.session.execute(
            select(Expense.expense_type_code, func.sum(Expense.amount)).group_by(
                Expense.expense_type_code
            )
        )
        by_type = {row[0]: float(row[1] or 0) for row in by_type_result.all()}

        # By region
        by_region_result = await self.session.execute(
            select(Expense.region_id, func.sum(Expense.amount))
            .where(Expense.region_id.isnot(None))
            .group_by(Expense.region_id)
        )
        by_region = {str(row[0]): float(row[1] or 0) for row in by_region_result.all()}

        # By service
        by_service_result = await self.session.execute(
            select(Expense.service_id, func.sum(Expense.amount))
            .where(Expense.service_id.isnot(None))
            .group_by(Expense.service_id)
        )
        by_service = {
            str(row[0]): float(row[1] or 0) for row in by_service_result.all()
        }

        return {
            "total_amount": total_amount,
            "total_count": total_count,
            "by_type": by_type,
            "by_region": by_region,
            "by_service": by_service,
        }

    async def get_total_amount(self) -> float:
        """Backward-compatible total amount."""
        stats = await self.get_statistics()
        return float(stats["total_amount"])

    async def count(self) -> int:
        """Backward-compatible total count."""
        stats = await self.get_statistics()
        return int(stats["total_count"])

    async def get_total_by_type(self) -> dict[str, float]:
        """Backward-compatible grouped total by type."""
        stats = await self.get_statistics()
        return stats["by_type"]

    async def get_total_by_region(self) -> dict[str, float]:
        """Backward-compatible grouped total by region."""
        stats = await self.get_statistics()
        return stats["by_region"]

    async def get_total_by_service(self) -> dict[str, float]:
        """Backward-compatible grouped total by service."""
        stats = await self.get_statistics()
        return stats["by_service"]

    async def get_recent(self, days: int = 30) -> list[Expense]:
        """Backward-compatible recent expenses query."""
        cutoff = datetime.now() - timedelta(days=days)
        result = await self.session.execute(
            select(Expense)
            .where(Expense.occurred_at >= cutoff)
            .order_by(desc(Expense.occurred_at))
        )
        return list(result.scalars().all())
