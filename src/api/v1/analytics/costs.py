from fastapi import APIRouter, Depends, Request

from api.dependencies.analytics import get_cost_analytics_service
from core.cache.decorators import cached
from core.config import get_settings
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.costs import (
    AssetCostAnalyticsOut,
    RegionCostAnalyticsOut,
    RepairCostAnalyticsOut,
)
from schemas.pagination import PageOutSchema, PaginationParamsSchema
from services.analytics.cost_analytics_service import CostAnalyticsService
from utils.analytics.cache_utils import run_analytics_operation

router = APIRouter(prefix="/analytics/costs", tags=["Analytics - Costs"])
settings = get_settings()


@router.get(
    "/repairs",
    response_model=PageOutSchema[RepairCostAnalyticsOut],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:costs:repairs",))
async def get_repair_costs(
    request: Request,
    pagination: PaginationParamsSchema = Depends(),
    service: CostAnalyticsService = Depends(get_cost_analytics_service),
):
    return await run_analytics_operation(
        request,
        "analytics.costs.repairs",
        {"page": pagination.page, "limit": pagination.limit},
        lambda: service.get_repair_costs(pagination),
        lambda: PageOutSchema(
            items=[], total=0, page=pagination.page, limit=pagination.limit
        ),
    )


@router.get(
    "/assets",
    response_model=PageOutSchema[AssetCostAnalyticsOut],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:costs:assets",))
async def get_asset_costs(
    request: Request,
    pagination: PaginationParamsSchema = Depends(),
    service: CostAnalyticsService = Depends(get_cost_analytics_service),
):
    return await run_analytics_operation(
        request,
        "analytics.costs.assets",
        {"page": pagination.page, "limit": pagination.limit},
        lambda: service.get_asset_costs(pagination),
        lambda: PageOutSchema(
            items=[], total=0, page=pagination.page, limit=pagination.limit
        ),
    )


@router.get(
    "/regions",
    response_model=PageOutSchema[RegionCostAnalyticsOut],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:costs:regions",))
async def get_region_costs(
    request: Request,
    pagination: PaginationParamsSchema = Depends(),
    service: CostAnalyticsService = Depends(get_cost_analytics_service),
):
    return await run_analytics_operation(
        request,
        "analytics.costs.regions",
        {"page": pagination.page, "limit": pagination.limit},
        lambda: service.get_region_costs(pagination),
        lambda: PageOutSchema(
            items=[], total=0, page=pagination.page, limit=pagination.limit
        ),
    )
