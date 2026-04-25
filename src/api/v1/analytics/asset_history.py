# api/v1/analytics/asset_history.py

from fastapi import APIRouter, Depends, Query, Request
from uuid import UUID

from schemas.analytics.asset_history import (
    AssetHistoryFilter,
    AssetHistoryPage,
    AssetHistoryAggregates,
    AssetHistoryOut,
)
from schemas.pagination import PaginationParams, PageOut
from services.analytics.asset_history_analytics_service import (
    AssetHistoryAnalyticsService,
)
from api.dependencies.analytics import get_asset_history_analytics_service
from api.v1.analytics._utils import enforce_rate_limit, parse_optional_datetime, parse_rate_limit, run_analytics_operation
from core.config import get_settings
from core.security.rbac import presets
from core.cache.decorators import cached
from schemas.pagination import build_page
from decimal import Decimal

router = APIRouter(
    prefix="/analytics/asset-history",
    tags=["Analytics - Asset History"],
)
settings = get_settings()
ANALYTICS_LIMIT, ANALYTICS_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS)


@router.get(
    "/",
    response_model=PageOut[AssetHistoryOut],
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=60, tags=("analytics:asset-history:list",))
async def list_asset_history(
    request: Request,
    asset_id: UUID | None = Query(None),
    user_id: UUID | None = Query(None),
    action: str | None = Query(None, max_length=50),
    date_from: str | None = Query(None, description="ISO format datetime"),
    date_to: str | None = Query(None, description="ISO format datetime"),
    search: str | None = Query(None, max_length=100),
    pagination: PaginationParams = Depends(),
    service: AssetHistoryAnalyticsService = Depends(get_asset_history_analytics_service),
):
    """List asset history with filtering and pagination."""
    date_from_dt = parse_optional_datetime(date_from)
    date_to_dt = parse_optional_datetime(date_to)

    filters = AssetHistoryFilter(
        asset_id=asset_id,
        user_id=user_id,
        action=action,
        date_from=date_from_dt,
        date_to=date_to_dt,
        search=search,
    )

    await enforce_rate_limit(request, "analytics:asset-history:list", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.asset_history.list",
        {"asset_id": asset_id, "user_id": user_id, "action": action, "date_from": date_from_dt, "date_to": date_to_dt, "search": search},
        lambda: service.list(filters, pagination),
        lambda: build_page(schema=PageOut[AssetHistoryOut], items=[], total=0, page=pagination.page, limit=pagination.limit),
    )


@router.get(
    "/aggregates",
    response_model=AssetHistoryAggregates,
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=600, tags=("analytics:asset-history:aggregates",))
async def get_asset_history_aggregates(
    request: Request,
    asset_id: UUID | None = Query(None),
    user_id: UUID | None = Query(None),
    action: str | None = Query(None, max_length=50),
    date_from: str | None = Query(None, description="ISO format datetime"),
    date_to: str | None = Query(None, description="ISO format datetime"),
    service: AssetHistoryAnalyticsService = Depends(get_asset_history_analytics_service),
):
    """Get aggregated asset history metrics."""
    date_from_dt = parse_optional_datetime(date_from)
    date_to_dt = parse_optional_datetime(date_to)

    filters = AssetHistoryFilter(
        asset_id=asset_id,
        user_id=user_id,
        action=action,
        date_from=date_from_dt,
        date_to=date_to_dt,
    )

    await enforce_rate_limit(request, "analytics:asset-history:aggregates", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.asset_history.aggregates",
        {"asset_id": asset_id, "user_id": user_id, "action": action, "date_from": date_from_dt, "date_to": date_to_dt},
        lambda: service.get_aggregates(filters),
        lambda: AssetHistoryAggregates(
            total_entries=0,
            unique_assets=0,
            unique_users=0,
            date_range_start=None,
            date_range_end=None,
            actions_breakdown=[],
            most_active_asset_id=None,
            most_active_asset_name=None,
            most_active_user_id=None,
            most_active_user_name=None,
        ),
    )


@router.post(
    "/search",
    response_model=PageOut[AssetHistoryOut],
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=60, tags=("analytics:asset-history:search",))
async def search_asset_history(
    request: Request,
    filters: AssetHistoryFilter,
    pagination: PaginationParams = Depends(),
    service: AssetHistoryAnalyticsService = Depends(get_asset_history_analytics_service),
):
    """Search asset history with complex filters."""
    await enforce_rate_limit(request, "analytics:asset-history:search", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.asset_history.search",
        filters.model_dump(mode="json"),
        lambda: service.list(filters, pagination),
        lambda: build_page(schema=PageOut[AssetHistoryOut], items=[], total=0, page=pagination.page, limit=pagination.limit),
    )
