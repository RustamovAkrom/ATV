from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from api.dependencies.analytics import get_asset_history_analytics_service
from api.v1.analytics._utils import parse_optional_datetime, run_analytics_operation
from core.cache.decorators import cached
from core.config import get_settings
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.asset_history import AssetHistoryAggregates, AssetHistoryFilter, AssetHistoryOut
from schemas.pagination import PageOutSchema, PaginationParamsSchema
from services.analytics.asset_history_analytics_service import AssetHistoryAnalyticsService

router = APIRouter(prefix="/analytics/asset-history", tags=["Analytics - History"])
settings = get_settings()


@router.get("/", response_model=PageOutSchema[AssetHistoryOut], dependencies=[Depends(AssetPermissions.CanViewAssets)])
@cached(ttl=60, tags=("analytics:history:list",))
async def list_asset_history(
    request: Request, asset_id: UUID | None = Query(None), user_id: UUID | None = Query(None),
    action: str | None = Query(None, max_length=50), date_from: str | None = Query(None), date_to: str | None = Query(None),
    search: str | None = Query(None, max_length=100), pagination: PaginationParamsSchema = Depends(),
    service: AssetHistoryAnalyticsService = Depends(get_asset_history_analytics_service),
):
    filters = AssetHistoryFilter(
        asset_id=asset_id, user_id=user_id, action=action,
        date_from=parse_optional_datetime(date_from), date_to=parse_optional_datetime(date_to), search=search,
    )
    return await run_analytics_operation(
        request, "analytics.history.list", filters.model_dump(mode="json"),
        lambda: service.list(filters, pagination),
        lambda: PageOutSchema([], 0, pagination.page, pagination.limit),
    )


@router.get("/aggregates", response_model=AssetHistoryAggregates, dependencies=[Depends(AssetPermissions.CanViewAssets)])
@cached(ttl=600, tags=("analytics:history:aggregates",))
async def get_asset_history_aggregates(
    request: Request, asset_id: UUID | None = Query(None), user_id: UUID | None = Query(None),
    action: str | None = Query(None, max_length=50), date_from: str | None = Query(None), date_to: str | None = Query(None),
    service: AssetHistoryAnalyticsService = Depends(get_asset_history_analytics_service),
):
    filters = AssetHistoryFilter(
        asset_id=asset_id, user_id=user_id, action=action,
        date_from=parse_optional_datetime(date_from), date_to=parse_optional_datetime(date_to),
    )
    return await run_analytics_operation(
        request, "analytics.history.aggregates", filters.model_dump(mode="json"),
        lambda: service.get_aggregates(filters),
        lambda: AssetHistoryAggregates(total_entries=0, unique_assets=0, unique_users=0, date_range_start=None, date_range_end=None, actions_breakdown=[], most_active_asset_id=None, most_active_asset_name=None, most_active_user_id=None, most_active_user_name=None),
    )
