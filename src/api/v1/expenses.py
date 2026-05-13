"""API endpoints for expenses management."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.security.auth.dependencies import get_current_user
from db.dependencies import get_db_session
from core.security.rbac.presets import ExpensePermission
from schemas.common import StatusResponse
from schemas.expenses import (
    ExpenseCreateSchema,
    ExpenseOutSchema,
    ExpensePageSchema,
    ExpenseStatsSchema,
    ExpenseUpdateSchema,
)
from services.expense_service import ExpenseService
from schemas.auth.auth import CurrentUserSchema

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get(
    "/",
    response_model=ExpensePageSchema,
    dependencies=[Depends(ExpensePermission.CanViewExpenses)],
)
async def list_expenses(
    db=Depends(get_db_session),
    _: CurrentUserSchema = Depends(get_current_user),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    expense_type: str | None = None,
    region_id: UUID | None = None,
    service_id: UUID | None = None,
    asset_id: UUID | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):
    """List all expenses with filters and pagination."""
    service = ExpenseService(db)
    return await service.list_expenses(
        page=page,
        size=size,
        expense_type=expense_type,
        region_id=region_id,
        service_id=service_id,
        asset_id=asset_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.post(
    "/",
    response_model=ExpenseOutSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ExpensePermission.CanCreateExpenses)],
)
async def create_expense(
    data: ExpenseCreateSchema,
    db: AsyncSession = Depends(get_db_session),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Create a new expense."""
    service = ExpenseService(db)
    return await service.create_expense(data, current_user.id)


@router.get(
    "/{expense_id}",
    response_model=ExpenseOutSchema,
    dependencies=[Depends(ExpensePermission.CanViewExpenses)],
)
async def get_expense(
    expense_id: UUID,
    db: AsyncSession =Depends(get_db_session),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Get a specific expense by ID."""
    service = ExpenseService(db)
    return await service.get_expense(expense_id)


@router.patch(
    "/{expense_id}",
    response_model=ExpenseOutSchema,
    dependencies=[Depends(ExpensePermission.CanUpdateExpenses)],
)
async def update_expense(
    expense_id: UUID,
    data: ExpenseUpdateSchema,
    db: AsyncSession = Depends(get_db_session),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Update an expense."""
    service = ExpenseService(db)
    return await service.update_expense(expense_id, data)


@router.delete(
    "/{expense_id}",
    response_model=StatusResponse,
    dependencies=[Depends(ExpensePermission.CanDeleteExpenses)],
)
async def delete_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Delete an expense."""
    service = ExpenseService(db)
    await service.delete_expense(expense_id)
    return StatusResponse(status="deleted", message="Expense deleted successfully")


@router.get(
    "/asset/{asset_id}/expenses",
    response_model=list[ExpenseOutSchema],
    dependencies=[Depends(ExpensePermission.CanViewExpenses)],
)
async def get_asset_expenses(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Get all expenses for a specific asset."""
    service = ExpenseService(db)
    return await service.get_by_asset(asset_id)


@router.get(
    "/repair/{repair_id}/expenses",
    response_model=list[ExpenseOutSchema],
    dependencies=[Depends(ExpensePermission.CanViewExpenses)],
)
async def get_repair_expenses(
    repair_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Get all expenses for a specific repair."""
    service = ExpenseService(db)
    return await service.get_by_repair(repair_id)


@router.get(
    "/region/{region_id}/summary",
    response_model=list[ExpenseOutSchema],
    dependencies=[Depends(ExpensePermission.CanViewExpenses)],
)
async def get_region_expenses(
    region_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Get all expenses for a specific region."""
    service = ExpenseService(db)
    return await service.get_by_region(region_id)


@router.get(
    "/statistics",
    response_model=ExpenseStatsSchema,
    dependencies=[Depends(ExpensePermission.CanViewExpenses)],
)
async def get_expense_statistics(
    db: AsyncSession = Depends(get_db_session),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Get expense statistics and aggregations."""
    service = ExpenseService(db)
    return await service.get_statistics()
