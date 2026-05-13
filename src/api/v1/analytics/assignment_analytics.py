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
from core.security.rbac.presets import AssetPermissions
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

router = APIRouter(prefix="/analytics/assignments", tags=["Analytics - Assignments"])
settings = get_settings()
ANALYTICS_LIMIT, ANALYTICS_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS)


@router.get(
    "/",
    response_model=PageOutSchema[AssetAssignmentDetailOut],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=60, tags=("analytics:assignments:list",))
async def list_assignments(
    request: Request,
    asset_id: UUID | None = Query(None),
    user_id: UUID | None = Query(None),
    status: AssignmentAnalyticsStatus | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    search: str | None = Query(None, max_length=100),
    pagination: PaginationParamsSchema = Depends(),
    service: AssetAssignmentAnalyticsService = Depends(get_asset_assignment_analytics_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    filters = AssetAssignmentFilterInput(
        asset_id=asset_id,
        user_id=user_id,
        status=status,
        date_from=parse_optional_datetime(date_from),
        date_to=parse_optional_datetime(date_to),
        search=search,
    )
    await enforce_rate_limit(request, "analytics:assignments:list", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.assignments.list",
        filters.model_dump(mode="json"),
        lambda: service.list_assignments(filters, pagination, current_user),
        lambda: build_page(PageOutSchema[AssetAssignmentDetailOut], [], 0, pagination.page, pagination.limit),
    )


@router.get(
    "/active",
    response_model=PageOutSchema[AssetAssignmentDetailOut],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=30, tags=("analytics:assignments:active",))
async def list_active_assignments(
    request: Request,
    pagination: PaginationParamsSchema = Depends(),
    service: AssetAssignmentAnalyticsService = Depends(get_asset_assignment_analytics_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    await enforce_rate_limit(request, "analytics:assignments:active", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.assignments.active",
        {"page": pagination.page, "limit": pagination.limit},
        lambda: service.list_active_assignments(pagination, current_user),
        lambda: build_page(PageOutSchema[AssetAssignmentDetailOut], [], 0, pagination.page, pagination.limit),
    )


@router.get(
    "/user/{user_id}/summary",
    response_model=UserAssignmentSummary,
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:assignments:user",))
async def get_user_assignment_summary(
    request: Request,
    user_id: UUID,
    service: AssetAssignmentAnalyticsService = Depends(get_asset_assignment_analytics_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    await enforce_rate_limit(request, "analytics:assignments:user-summary", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
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
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:assignments:timeline",))
async def get_asset_assignment_timeline(
    request: Request,
    asset_id: UUID,
    service: AssetAssignmentAnalyticsService = Depends(get_asset_assignment_analytics_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    await enforce_rate_limit(request, "analytics:assignments:timeline", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
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
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=600, tags=("analytics:assignments:aggregates",))
async def get_assignment_aggregates(
    request: Request,
    asset_id: UUID | None = Query(None),
    user_id: UUID | None = Query(None),
    status: AssignmentAnalyticsStatus | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    service: AssetAssignmentAnalyticsService = Depends(get_asset_assignment_analytics_service),
):
    filters = AssetAssignmentFilterInput(
        asset_id=asset_id,
        user_id=user_id,
        status=status,
        date_from=parse_optional_datetime(date_from),
        date_to=parse_optional_datetime(date_to),
    )
    await enforce_rate_limit(request, "analytics:assignments:aggregates", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.assignments.aggregates",
        filters.model_dump(mode="json"),
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
