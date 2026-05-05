from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies.analytics import get_extended_region_analytics_service
from api.v1.analytics._utils import (
    enforce_rate_limit,
    parse_rate_limit,
    run_analytics_operation,
)
from core.cache.decorators import cached
from core.config import get_settings
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.regions import (
    RegionDetailsOut,
    RegionHeatmapPointOut,
    RegionOverviewOut,
)
from services.analytics.region_analytics_service import RegionAnalyticsService

router = APIRouter(prefix="/analytics/regions", tags=["Analytics - Regions"])
settings = get_settings()
ANALYTICS_LIMIT, ANALYTICS_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS)


@router.get(
    "/overview",
    response_model=list[RegionOverviewOut],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:regions:overview",))
async def get_regions_overview(
    request: Request,
    service: RegionAnalyticsService = Depends(get_extended_region_analytics_service),
):
    await enforce_rate_limit(
        request, "analytics:regions:overview", ANALYTICS_LIMIT, ANALYTICS_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.regions.overview",
        {},
        lambda: service.get_overview(),
        lambda: [],
    )


@router.get(
    "/{region_id}/details",
    response_model=RegionDetailsOut | None,
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=180, tags=("analytics:regions:details",))
async def get_region_details(
    request: Request,
    region_id: UUID,
    service: RegionAnalyticsService = Depends(get_extended_region_analytics_service),
):
    await enforce_rate_limit(
        request, "analytics:regions:details", ANALYTICS_LIMIT, ANALYTICS_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.regions.details",
        {"region_id": region_id},
        lambda: service.get_details(region_id),
        lambda: RegionDetailsOut(
            region_id=region_id,
            region_name="Unknown",
            latitude=None,
            longitude=None,
            geojson=None,
            asset_counts={
                "active": 0,
                "assigned": 0,
                "in_repair": 0,
                "archived": 0,
                "total": 0,
            },
            transfers_in=0,
            transfers_out=0,
            repairs_count=0,
            assignment_load=0,
            services=[],
            top_cost_assets=[],
        ),
    )


@router.get(
    "/heatmap",
    response_model=list[RegionHeatmapPointOut],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:regions:heatmap",))
async def get_region_heatmap(
    request: Request,
    service: RegionAnalyticsService = Depends(get_extended_region_analytics_service),
):
    await enforce_rate_limit(
        request, "analytics:regions:heatmap", ANALYTICS_LIMIT, ANALYTICS_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.regions.heatmap",
        {},
        lambda: service.get_heatmap(),
        lambda: [],
    )
