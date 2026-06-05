"""API endpoints for expenses management."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from api.dependencies.assets.asset_expense import get_expense_service
from core.cache.decorators import cached, invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import ExpensePermission
from core.slowapi import limiter
from schemas.assets.expenses import (
    ExpenseCreateSchema,
    ExpenseOutSchema,
    ExpensePageSchema,
    ExpenseStatsSchema,
    ExpenseUpdateSchema,
)
from schemas.auth import CurrentUserSchema
from schemas.common import StatusResponse
from services.assets.expense_service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get(
    "/statistics",
    response_model=ExpenseStatsSchema,
    dependencies=[Depends(ExpensePermission.CanViewExpenses)],
)
@cached(tags=("expense:statistics",))
async def get_expense_statistics(
    service: ExpenseService = Depends(get_expense_service),
    _: CurrentUserSchema = Depends(get_current_user),
) -> ExpenseStatsSchema:
    """Get expense statistics and aggregations."""
    return await service.get_statistics()


@router.get(
    "/",
    response_model=ExpensePageSchema,
    dependencies=[Depends(ExpensePermission.CanViewExpenses)],
)
@cached(tags=("expense:list",))
async def list_expenses(
    request: Request,
    service: ExpenseService = Depends(get_expense_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    expense_type: str | None = None,
    department_id: UUID | None = None,
    region_id: UUID | None = None,
    service_id: UUID | None = None,
    asset_id: UUID | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> ExpensePageSchema:
    """List all expenses with filters and pagination."""
    return await service.list(
        actor=current_user,
        page=page,
        limit=limit,
        expense_type=expense_type,
        department_id=department_id,
        region_id=region_id,
        service_id=service_id,
        asset_id=asset_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/asset/{asset_id}",
    response_model=list[ExpenseOutSchema],
    dependencies=[Depends(ExpensePermission.CanViewExpenses)],
)
@cached(tags=("expense:asset:detail",))
async def get_asset_expenses(
    asset_id: UUID,
    service: ExpenseService = Depends(get_expense_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
) -> list[ExpenseOutSchema]:
    """Get all expenses for a specific asset."""
    return await service.get_by_asset(asset_id, current_user)


@router.get(
    "/repair/{repair_id}",
    response_model=list[ExpenseOutSchema],
    dependencies=[Depends(ExpensePermission.CanViewExpenses)],
)
@cached(tags=("expense:repair:detail",))
async def get_repair_expenses(
    repair_id: UUID,
    service: ExpenseService = Depends(get_expense_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
) -> list[ExpenseOutSchema]:
    """Get all expenses for a specific repair."""
    return await service.get_by_repair(repair_id, current_user)


@router.get(
    "/{expense_id}",
    response_model=ExpenseOutSchema,
    dependencies=[Depends(ExpensePermission.CanViewExpenses)],
)
@cached(tags=("expense:detail",))
async def get_expense(
    expense_id: UUID,
    service: ExpenseService = Depends(get_expense_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
) -> ExpenseOutSchema:
    """Get a specific expense by ID."""
    return await service.get(expense_id, current_user)


@router.post(
    "/",
    response_model=ExpenseOutSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ExpensePermission.CanCreateExpenses)],
)
@limiter.limit("20/minute")
@invalidate_cache(
    tags=(
        "expense:statistics",
        "expense:list",
    )
)
async def create_expense(
    request: Request,
    data: ExpenseCreateSchema,
    service: ExpenseService = Depends(get_expense_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
) -> ExpenseOutSchema:
    """Create a new expense."""
    return await service.create(data, current_user)


@router.patch(
    "/{expense_id}",
    response_model=ExpenseOutSchema,
    dependencies=[Depends(ExpensePermission.CanUpdateExpenses)],
)
@limiter.limit("30/minute")
@invalidate_cache(
    tags=(
        "expense:statistics",
        "expense:list",
        "expense:asset:detail",
        "expense:repair:detail",
        "expense:detail",
    )
)
async def update_expense(
    request: Request,
    expense_id: UUID,
    data: ExpenseUpdateSchema,
    service: ExpenseService = Depends(get_expense_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
) -> ExpenseOutSchema:
    """Update an expense."""
    return await service.update(expense_id, data, current_user)


@router.delete(
    "/{expense_id}",
    response_model=StatusResponse,
    dependencies=[Depends(ExpensePermission.CanDeleteExpenses)],
)
@limiter.limit("10/minute")
@invalidate_cache(
    tags=(
        "expense:statistics",
        "expense:list",
        "expense:asset:detail",
        "expense:repair:detail",
        "expense:detail",
    )
)
async def delete_expense(
    request: Request,
    expense_id: UUID,
    service: ExpenseService = Depends(get_expense_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
) -> StatusResponse:
    """Delete an expense."""
    await service.delete(expense_id, current_user)
    return StatusResponse(status="deleted", message="Expense deleted successfully")
