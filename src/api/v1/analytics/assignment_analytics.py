# api/v1/analytics/assignment_analytics.py

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from api.dependencies.analytics import get_asset_assignment_analytics_service
from api.v1.analytics._utils import (
    enforce_rate_limit,
    parse_optional_datetime,
    parse_rate_limit,
    run_analytics_operation,
)
from core.cache.decorators import cached
from core.config import get_settings
from core.security.auth.dependencies import get_current_user
from core.security.rbac import presets
from schemas.analytics.asset_assignment_analytics import (
    AssetAssignmentDetailOut,
    AssetAssignmentFilterInput,
    AssetAssignmentTimeline,
    AssignmentAggregates,
    AssignmentAnalyticsStatus,
    UserAssignmentSummary,
)
from schemas.auth import CurrentUserSchema
from schemas.pagination import PageOutSchema, PaginationParamsSchema, build_page
from services.analytics.asset_assignment_analytics_service import (
    AssetAssignmentAnalyticsService,
)

router = APIRouter(
    prefix="/analytics/assignments",
    tags=["Analytics - Asset Assignments"],
)
settings = get_settings()
ANALYTICS_LIMIT, ANALYTICS_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS)


@router.get(
    "/",
    response_model=PageOutSchema[AssetAssignmentDetailOut],
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=60, tags=("analytics:assignments:list",))
async def list_assignments(
    request: Request,
    asset_id: UUID | None = Query(None),
    user_id: UUID | None = Query(None),
    status: AssignmentAnalyticsStatus | None = Query(
        None, description="active or inactive"
    ),
    date_from: str | None = Query(None, description="ISO format datetime"),
    date_to: str | None = Query(None, description="ISO format datetime"),
    search: str | None = Query(None, max_length=100),
    pagination: PaginationParamsSchema = Depends(),
    service: AssetAssignmentAnalyticsService = Depends(
        get_asset_assignment_analytics_service
    ),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """List asset assignments with filtering and pagination."""
    date_from_dt = parse_optional_datetime(date_from)
    date_to_dt = parse_optional_datetime(date_to)

    filters = AssetAssignmentFilterInput(
        asset_id=asset_id,
        user_id=user_id,
        status=status,
        date_from=date_from_dt,
        date_to=date_to_dt,
        search=search,
    )

    await enforce_rate_limit(
        request, "analytics:assignments:list", ANALYTICS_LIMIT, ANALYTICS_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.assignments.list",
        {
            "asset_id": asset_id,
            "user_id": user_id,
            "status": status,
            "date_from": date_from_dt,
            "date_to": date_to_dt,
            "search": search,
        },
        lambda: service.list_assignments(filters, pagination, current_user),
        lambda: build_page(
            schema=PageOutSchema[AssetAssignmentDetailOut],
            items=[],
            total=0,
            page=pagination.page,
            limit=pagination.limit,
        ),
    )


@router.get(
    "/active",
    response_model=PageOutSchema[AssetAssignmentDetailOut],
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=30, tags=("analytics:assignments:active",))
async def list_active_assignments(
    request: Request,
    pagination: PaginationParamsSchema = Depends(),
    service: AssetAssignmentAnalyticsService = Depends(
        get_asset_assignment_analytics_service
    ),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """List currently active assignments."""
    await enforce_rate_limit(
        request, "analytics:assignments:active", ANALYTICS_LIMIT, ANALYTICS_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.assignments.active",
        {"page": pagination.page, "limit": pagination.limit},
        lambda: service.list_active_assignments(pagination, current_user),
        lambda: build_page(
            schema=PageOutSchema[AssetAssignmentDetailOut],
            items=[],
            total=0,
            page=pagination.page,
            limit=pagination.limit,
        ),
    )


@router.get(
    "/user/{user_id}/summary",
    response_model=UserAssignmentSummary,
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=300, tags=("analytics:assignments:user",))
async def get_user_assignment_summary(
    request: Request,
    user_id: UUID,
    service: AssetAssignmentAnalyticsService = Depends(
        get_asset_assignment_analytics_service
    ),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Get assignment summary for a specific user."""
    await enforce_rate_limit(
        request, "analytics:assignments:user-summary", ANALYTICS_LIMIT, ANALYTICS_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.assignments.user_summary",
        {"user_id": user_id},
        lambda: service.get_user_summary(user_id, current_user),
        lambda: UserAssignmentSummary(
            user_id=user_id,
            user_name="Unknown",
            user_email="",
            active_assignments_count=0,
            total_assignments_count=0,
            average_duration_days=Decimal(0),
            longest_assignment_days=Decimal(0),
            recent_assignment_date=None,
        ),
    )


@router.get(
    "/asset/{asset_id}/timeline",
    response_model=AssetAssignmentTimeline,
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=300, tags=("analytics:assignments:timeline",))
async def get_asset_assignment_timeline(
    request: Request,
    asset_id: UUID,
    service: AssetAssignmentAnalyticsService = Depends(
        get_asset_assignment_analytics_service
    ),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Get complete assignment timeline for an asset."""
    await enforce_rate_limit(
        request, "analytics:assignments:timeline", ANALYTICS_LIMIT, ANALYTICS_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.assignments.timeline",
        {"asset_id": asset_id},
        lambda: service.get_asset_timeline(asset_id, current_user),
        lambda: AssetAssignmentTimeline(
            asset_id=asset_id,
            asset_name="Unknown",
            total_assignments=0,
            active_assignment=None,
            timeline=[],
        ),
    )


@router.get(
    "/aggregates",
    response_model=AssignmentAggregates,
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=600, tags=("analytics:assignments:aggregates",))
async def get_assignment_aggregates(
    request: Request,
    asset_id: UUID | None = Query(None),
    user_id: UUID | None = Query(None),
    status: AssignmentAnalyticsStatus | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    service: AssetAssignmentAnalyticsService = Depends(
        get_asset_assignment_analytics_service
    ),
):
    """Get aggregated assignment metrics."""
    date_from_dt = parse_optional_datetime(date_from)
    date_to_dt = parse_optional_datetime(date_to)

    filters = AssetAssignmentFilterInput(
        asset_id=asset_id,
        user_id=user_id,
        status=status,
        date_from=date_from_dt,
        date_to=date_to_dt,
    )

    await enforce_rate_limit(
        request, "analytics:assignments:aggregates", ANALYTICS_LIMIT, ANALYTICS_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.assignments.aggregates",
        {
            "asset_id": asset_id,
            "user_id": user_id,
            "status": status,
            "date_from": date_from_dt,
            "date_to": date_to_dt,
        },
        lambda: service.get_aggregates(filters),
        lambda: AssignmentAggregates(
            total_active_assignments=0,
            total_inactive_assignments=0,
            total_assignments=0,
            average_assignment_duration_days=Decimal(0),
            longest_assignment_duration_days=Decimal(0),
            most_frequently_assigned_asset_id=None,
            most_frequently_assigned_asset_name=None,
            most_active_user_id=None,
            most_active_user_name=None,
        ),
    )
