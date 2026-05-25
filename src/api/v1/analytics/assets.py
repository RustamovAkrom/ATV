from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies.analytics import get_asset_analytics_service, get_report_service
from core.cache.decorators import cached
from core.config import get_settings
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.common import (
    AnalyticsFilters,
    AnalyticsMetaSchema,
    AnalyticsResponseSchema,
)
from schemas.auth import CurrentUserSchema
from services.analytics.asset_analytics_service import AssetAnalyticsService
from services.analytics.report_service import ReportService
from utils.helpers import utc_now

router = APIRouter(prefix="/analytics/assets", tags=["Analytics - Assets"])
settings = get_settings()


def _filters(region_id, service_id, date_from, date_to) -> AnalyticsFilters:
    return AnalyticsFilters(
        region_id=region_id, service_id=service_id, date_from=date_from, date_to=date_to
    )


@router.get(
    "/distribution",
    response_model=AnalyticsResponseSchema,
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:assets:distribution",))
async def get_distribution(
    region_id: UUID | None = Query(None),
    service_id: UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetAnalyticsService = Depends(get_asset_analytics_service),
):
    filters = _filters(region_id, service_id, date_from, date_to)
    return AnalyticsResponseSchema(
        data=await service.distribution(filters, current_user),
        meta=AnalyticsMetaSchema(generated_at=utc_now(), filters=filters),
    )


@router.get(
    "/lifecycle",
    response_model=AnalyticsResponseSchema,
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:assets:lifecycle",))
async def get_lifecycle(
    region_id: UUID | None = Query(None),
    service_id: UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetAnalyticsService = Depends(get_asset_analytics_service),
):
    filters = _filters(region_id, service_id, date_from, date_to)
    return AnalyticsResponseSchema(
        data=await service.lifecycle(filters, current_user),
        meta=AnalyticsMetaSchema(generated_at=utc_now(), filters=filters),
    )


@router.get(
    "/overview",
    response_model=AnalyticsResponseSchema,
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:assets:overview",))
async def get_assets_overview(
    region_id: UUID | None = Query(None),
    service_id: UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    filters = _filters(region_id, service_id, date_from, date_to)
    return AnalyticsResponseSchema(
        data=await service.overview(filters, current_user),
        meta=AnalyticsMetaSchema(generated_at=utc_now(), filters=filters),
    )
