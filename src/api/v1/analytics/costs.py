from fastapi import APIRouter, Depends, Request

from api.dependencies.analytics import get_cost_analytics_service
from api.v1.analytics._utils import enforce_rate_limit, parse_rate_limit, run_analytics_operation
from core.cache.decorators import cached
from core.config import get_settings
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.costs import AssetCostAnalyticsOut, RegionCostAnalyticsOut, RepairCostAnalyticsOut
from schemas.pagination import PageOutSchema, PaginationParamsSchema, build_page
from services.analytics.cost_analytics_service import CostAnalyticsService

router = APIRouter(prefix="/analytics/costs", tags=["Analytics - Costs"])
settings = get_settings()
ANALYTICS_LIMIT, ANALYTICS_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS)


@router.get("/repairs", response_model=PageOutSchema[RepairCostAnalyticsOut], dependencies=[Depends(AssetPermissions.CanViewAssets)])
@cached(ttl=300, tags=("analytics:costs:repairs",))
async def get_repair_costs(
    request: Request, pagination: PaginationParamsSchema = Depends(),
    service: CostAnalyticsService = Depends(get_cost_analytics_service),
):
    await enforce_rate_limit(request, "analytics:costs:repairs", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request, "analytics.costs.repairs", {"page": pagination.page, "limit": pagination.limit},
        lambda: service.get_repair_costs(pagination),
        lambda: build_page(PageOutSchema[RepairCostAnalyticsOut], [], 0, pagination.page, pagination.limit),
    )


@router.get("/assets", response_model=PageOutSchema[AssetCostAnalyticsOut], dependencies=[Depends(AssetPermissions.CanViewAssets)])
@cached(ttl=300, tags=("analytics:costs:assets",))
async def get_asset_costs(
    request: Request, pagination: PaginationParamsSchema = Depends(),
    service: CostAnalyticsService = Depends(get_cost_analytics_service),
):
    await enforce_rate_limit(request, "analytics:costs:assets", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request, "analytics.costs.assets", {"page": pagination.page, "limit": pagination.limit},
        lambda: service.get_asset_costs(pagination),
        lambda: build_page(PageOutSchema[AssetCostAnalyticsOut], [], 0, pagination.page, pagination.limit),
    )


@router.get("/regions", response_model=PageOutSchema[RegionCostAnalyticsOut], dependencies=[Depends(AssetPermissions.CanViewAssets)])
@cached(ttl=300, tags=("analytics:costs:regions",))
async def get_region_costs(
    request: Request, pagination: PaginationParamsSchema = Depends(),
    service: CostAnalyticsService = Depends(get_cost_analytics_service),
):
    await enforce_rate_limit(request, "analytics:costs:regions", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request, "analytics.costs.regions", {"page": pagination.page, "limit": pagination.limit},
        lambda: service.get_region_costs(pagination),
        lambda: build_page(PageOutSchema[RegionCostAnalyticsOut], [], 0, pagination.page, pagination.limit),
    )
