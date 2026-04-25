from fastapi import APIRouter, Depends, Request

from api.dependencies.analytics import get_cost_analytics_service
from api.v1.analytics._utils import enforce_rate_limit, parse_rate_limit, run_analytics_operation
from core.cache.decorators import cached
from core.config import get_settings
from core.security.rbac import presets
from schemas.analytics.costs import (
    AssetCostAnalyticsOut,
    RegionCostAnalyticsOut,
    RepairCostAnalyticsOut,
)
from schemas.pagination import PageOut, PaginationParams, build_page
from services.analytics.cost_analytics_service import CostAnalyticsService

router = APIRouter(prefix="/analytics/costs", tags=["Analytics - Costs"])
settings = get_settings()
ANALYTICS_LIMIT, ANALYTICS_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS)


@router.get("/repairs", response_model=PageOut[RepairCostAnalyticsOut], dependencies=[presets.CanViewAssets])
@cached(ttl=300, tags=("analytics:costs:repairs",))
async def get_repair_costs(
    request: Request,
    pagination: PaginationParams = Depends(),
    service: CostAnalyticsService = Depends(get_cost_analytics_service),
):
    await enforce_rate_limit(request, "analytics:costs:repairs", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.costs.repairs",
        {"page": pagination.page, "limit": pagination.limit},
        lambda: service.get_repair_costs(pagination),
        lambda: build_page(schema=PageOut[RepairCostAnalyticsOut], items=[], total=0, page=pagination.page, limit=pagination.limit),
    )


@router.get("/assets", response_model=PageOut[AssetCostAnalyticsOut], dependencies=[presets.CanViewAssets])
@cached(ttl=300, tags=("analytics:costs:assets",))
async def get_asset_costs(
    request: Request,
    pagination: PaginationParams = Depends(),
    service: CostAnalyticsService = Depends(get_cost_analytics_service),
):
    await enforce_rate_limit(request, "analytics:costs:assets", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.costs.assets",
        {"page": pagination.page, "limit": pagination.limit},
        lambda: service.get_asset_costs(pagination),
        lambda: build_page(schema=PageOut[AssetCostAnalyticsOut], items=[], total=0, page=pagination.page, limit=pagination.limit),
    )


@router.get("/regions", response_model=PageOut[RegionCostAnalyticsOut], dependencies=[presets.CanViewAssets])
@cached(ttl=300, tags=("analytics:costs:regions",))
async def get_region_costs(
    request: Request,
    pagination: PaginationParams = Depends(),
    service: CostAnalyticsService = Depends(get_cost_analytics_service),
):
    await enforce_rate_limit(request, "analytics:costs:regions", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.costs.regions",
        {"page": pagination.page, "limit": pagination.limit},
        lambda: service.get_region_costs(pagination),
        lambda: build_page(schema=PageOut[RegionCostAnalyticsOut], items=[], total=0, page=pagination.page, limit=pagination.limit),
    )
