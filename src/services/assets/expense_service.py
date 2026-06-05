"""Service for expenses management."""

import builtins
from datetime import datetime
from uuid import UUID

from core.exceptions.errors import NotFound
from core.security.access_control import AccessControl
from db.models.enums import UserRole
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
from utils.department import normalize_department_scope


class ExpenseService:
    """Service for managing expenses."""

    def __init__(self, repo: ExpenseRepository) -> None:
        """Initialize service with repository."""
        self.repo = repo

    @staticmethod
    def _to_uuid(value: UUID | str | None) -> UUID | None:
        if value is None:
            return None
        return UUID(str(value))

    async def _check_expense_access(
        self, expense_id: UUID, actor: CurrentUserSchema
    ) -> None:
        """Check if actor has access to expense."""
        expense = await self.repo.get(expense_id)
        if not expense:
            raise NotFound(f"Expense {expense_id} not found")

        AccessControl.check_scope_access(
            actor,
            getattr(expense, "department_id", None),
            getattr(expense, "region_id", None),
            getattr(expense, "service_id", None),
        )

    async def _check_asset_access(
        self, asset_id: UUID, actor: CurrentUserSchema
    ) -> None:
        """Check if actor has access to asset."""
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound(f"Asset {asset_id} not found")
        AccessControl.check_scope_access(
            actor,
            getattr(asset, "department_id", None),
            getattr(asset, "region_id", None),
            getattr(asset, "service_id", None),
        )

    async def create(
        self, data: ExpenseCreateSchema, actor: CurrentUserSchema
    ) -> ExpenseOutSchema:
        """Create a new expense."""
        payload = data.model_dump(exclude_unset=True)
        payload = await normalize_department_scope(
            getattr(self.repo, "session", None), payload
        )

        AccessControl.check_scope_access(
            actor,
            payload.get("department_id"),
            payload.get("region_id"),
            payload.get("service_id"),
        )

        if payload.get("asset_id"):
            await self._check_asset_access(payload["asset_id"], actor)
        if payload.get("repair_id"):
            repair = await self.repo.get_repair(payload["repair_id"])
            if not repair:
                raise NotFound(f"Repair {payload['repair_id']} not found")
            await self._check_asset_access(repair.asset_id, actor)
        expense = await self.repo.create(ExpenseCreateSchema(**payload), actor.id)
        return await self._to_out(expense)

    async def get(self, expense_id: UUID, actor: CurrentUserSchema) -> ExpenseOutSchema:
        """Get an expense by ID."""
        expense = await self.repo.get(expense_id)
        if not expense:
            raise NotFound(f"Expense {expense_id} not found")

        AccessControl.check_scope_access(
            actor,
            getattr(expense, "department_id", None),
            getattr(expense, "region_id", None),
            getattr(expense, "service_id", None),
        )

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
        department_id: UUID | None = None,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        asset_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> ExpensePageSchema:
        """List expenses with pagination and filters."""

        if actor.role != UserRole.SUPERADMIN.value:
            department_id, region_id, service_id = (
                AccessControl.normalize_scope_filters(
                    actor,
                    department_id,
                    region_id,
                    service_id,
                )
            )

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
        department_id = (
            actor.assigned_department_id if actor.assigned_department_id else None
        )
        AccessControl.check_scope_access(actor, department_id, region_id, None)
        expenses = await self.repo.get_by_region(region_id)
        return [await self._to_out(e) for e in expenses]

    async def get_statistics(self) -> ExpenseStatsSchema:
        """Get expense statistics."""
        stats = await self.repo.get_statistics()
        return ExpenseStatsSchema(**stats)

    async def _to_out(self, expense: Expense) -> ExpenseOutSchema:
        """Convert expense model to output schema."""
        created_by_id: UUID | None = getattr(expense, "created_by_id", None)
        created_by = getattr(expense, "created_by", None)
        if created_by_id is None and created_by is not None:
            created_by_id = getattr(created_by, "id", None)

        asset = getattr(expense, "asset", None)
        region = getattr(expense, "region", None)
        service = getattr(expense, "service", None)
        department = getattr(expense, "department", None)

        return ExpenseOutSchema(
            id=UUID(str(expense.id)),
            amount=expense.amount,
            currency=expense.currency,
            expense_type_code=expense.expense_type_code,
            description=expense.description,
            file_url=expense.file_url,
            asset=asset,
            repair_id=expense.repair_id,
            department_id=self._to_uuid(department.id)
            if department is not None
            else None,
            region=region,
            service=service,
            created_by_id=self._to_uuid(created_by_id),
            created_by_name=(
                getattr(created_by, "full_name", None)
                or getattr(created_by, "name", None)
                or getattr(created_by, "login", None)
                if created_by is not None
                else None
            ),
            occurred_at=expense.occurred_at,
            created_at=expense.created_at,
            updated_at=expense.updated_at,
        )
