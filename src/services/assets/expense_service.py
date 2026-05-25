"""Service for expenses management."""

import builtins
from uuid import UUID

from core.exceptions.errors import NotFound
from core.security.access_control import AccessControl
from db.models.expenses import Expense
from repositories.assets.expense_repo import ExpenseRepository
from schemas.assets.expenses import (
    ExpenseCreateSchema,
    ExpenseOutSchema,
    ExpensePageSchema,
    ExpenseStatsSchema,
    ExpenseUpdateSchema,
)
from schemas.auth.auth import CurrentUserSchema


class ExpenseService:
    """Service for managing expenses."""

    def __init__(self, repo: ExpenseRepository) -> None:
        """Initialize service with repository."""
        self.repo = repo

    async def _check_expense_access(
        self, expense_id: UUID, actor: CurrentUserSchema
    ) -> None:
        """Check if actor has access to expense."""
        expense = await self.repo.get(expense_id)
        if not expense:
            raise NotFound(f"Expense {expense_id} not found")

        if expense.region_id:
            AccessControl.check_region_access(actor, expense.region_id)
        if expense.service_id:
            AccessControl.check_service_access(actor, expense.service_id)

    async def _check_asset_access(
        self, asset_id: UUID, actor: CurrentUserSchema
    ) -> None:
        """Check if actor has access to asset."""
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound(f"Asset {asset_id} not found")
        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

    async def create(
        self, data: ExpenseCreateSchema, actor: CurrentUserSchema
    ) -> ExpenseOutSchema:
        """Create a new expense."""
        if data.asset_id:
            await self._check_asset_access(data.asset_id, actor)
        if data.repair_id:
            repair = await self.repo.get_repair(data.repair_id)
            if not repair:
                raise NotFound(f"Repair {data.repair_id} not found")
            await self._check_asset_access(repair.asset_id, actor)
        if data.region_id:
            AccessControl.check_region_access(actor, data.region_id)
        if data.service_id:
            AccessControl.check_service_access(actor, data.service_id)

        expense = await self.repo.create(data, actor.id)
        return await self._to_out(expense)

    async def get(self, expense_id: UUID, actor: CurrentUserSchema) -> ExpenseOutSchema:
        """Get an expense by ID."""
        expense = await self.repo.get(expense_id)
        if not expense:
            raise NotFound(f"Expense {expense_id} not found")

        if expense.region_id:
            AccessControl.check_region_access(actor, expense.region_id)
        if expense.service_id:
            AccessControl.check_service_access(actor, expense.service_id)

        return await self._to_out(expense)

    async def update(
        self, expense_id: UUID, data: ExpenseUpdateSchema, actor: CurrentUserSchema
    ) -> ExpenseOutSchema:
        """Update an expense."""
        await self._check_expense_access(expense_id, actor)

        expense = await self.repo.update(expense_id, data)
        if not expense:
            raise NotFound(f"Expense {expense_id} not found")

        return await self._to_out(expense)

    async def delete(self, expense_id: UUID, actor: CurrentUserSchema) -> None:
        """Delete an expense."""
        await self._check_expense_access(expense_id, actor)

        deleted = await self.repo.delete(expense_id)
        if not deleted:
            raise NotFound(f"Expense {expense_id} not found")

    async def list(
        self,
        actor: CurrentUserSchema,
        page: int = 1,
        limit: int = 20,
        expense_type: str | None = None,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        asset_id: UUID | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> ExpensePageSchema:
        """List expenses with pagination and filters."""
        from db.models.enums import UserRole

        if actor.role != UserRole.SUPERADMIN.value:
            region_id = actor.assigned_region_id or region_id
            service_id = actor.assigned_service_id or service_id

        items, total = await self.repo.list(
            page=page,
            limit=limit,
            expense_type=expense_type,
            region_id=region_id,
            service_id=service_id,
            asset_id=asset_id,
            start_date=start_date,
            end_date=end_date,
        )

        out_items = [await self._to_out(item) for item in items]

        return ExpensePageSchema(
            total=total,
            page=page,
            size=limit,
            items=out_items,
        )

    async def get_by_asset(
        self, asset_id: UUID, actor: CurrentUserSchema
    ) -> builtins.list[ExpenseOutSchema]:
        """Get all expenses for an asset."""
        await self._check_asset_access(asset_id, actor)
        expenses = await self.repo.get_by_asset(asset_id)
        return [await self._to_out(e) for e in expenses]

    async def get_by_repair(
        self, repair_id: UUID, actor: CurrentUserSchema
    ) -> builtins.list[ExpenseOutSchema]:
        """Get all expenses for a repair."""
        repair = await self.repo.get_repair(repair_id)
        if not repair:
            raise NotFound(f"Repair {repair_id} not found")
        await self._check_asset_access(repair.asset_id, actor)
        expenses = await self.repo.get_by_repair(repair_id)
        return [await self._to_out(e) for e in expenses]

    async def get_by_region(
        self, region_id: UUID, actor: CurrentUserSchema
    ) -> builtins.list[ExpenseOutSchema]:
        """Get all expenses for a region."""
        AccessControl.check_region_access(actor, region_id)
        expenses = await self.repo.get_by_region(region_id)
        return [await self._to_out(e) for e in expenses]

    async def get_statistics(self) -> ExpenseStatsSchema:
        """Get expense statistics."""
        stats = await self.repo.get_statistics()
        return ExpenseStatsSchema(**stats)

    async def _to_out(self, expense: Expense) -> ExpenseOutSchema:
        """Convert expense model to output schema."""
        created_by_id = (
            expense.created_by.id
            if hasattr(expense.created_by, "id")
            else expense.created_by
        )

        return ExpenseOutSchema(
            id=expense.id,
            amount=expense.amount,
            currency=expense.currency,
            expense_type_code=expense.expense_type_code,
            description=expense.description,
            file_url=expense.file_url,
            repair_id=expense.repair_id,
            created_by_id=created_by_id,
            occurred_at=expense.occurred_at,
            created_at=expense.created_at,
            updated_at=expense.updated_at,
        )
