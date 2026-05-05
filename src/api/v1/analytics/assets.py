from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies.analytics import (
    get_asset_analytics_domain_service,
    get_report_service,
)
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.common import AnalyticsFilters, AnalyticsMetaSchema, AnalyticsResponseSchema
from schemas.auth import CurrentUserSchema
from services.analytics.asset_analytics_service import AssetAnalyticsService
from services.analytics.report_service import ReportService
from utils.helpers import utc_now

router = APIRouter(prefix="/analytics/assets", tags=["Analytics - Assets"])


def _build_filters(
    region_id: UUID | None,
    service_id: UUID | None,
    date_from: date | None,
    date_to: date | None,
) -> AnalyticsFilters:
    return AnalyticsFilters(
        region_id=region_id, service_id=service_id, date_from=date_from, date_to=date_to
    )


def _meta(filters: AnalyticsFilters):
    return AnalyticsMetaSchema(generated_at=utc_now(), filters=filters)


@router.get("/distribution", response_model=AnalyticsResponseSchema, dependencies=[Depends(AssetPermissions.CanViewAssets)])
async def get_distribution(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetAnalyticsService = Depends(get_asset_analytics_domain_service),
):
    filters = _build_filters(region_id, service_id, date_from, date_to)
    return AnalyticsResponseSchema(data=await service.distribution(filters, current_user), meta=_meta(filters))


@router.get("/lifecycle", response_model=AnalyticsResponseSchema, dependencies=[Depends(AssetPermissions.CanViewAssets)])
async def get_lifecycle(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetAnalyticsService = Depends(get_asset_analytics_domain_service),
):
    filters = _build_filters(region_id, service_id, date_from, date_to)
    return AnalyticsResponseSchema(data=await service.lifecycle(filters, current_user), meta=_meta(filters))


@router.get("/overview", response_model=AnalyticsResponseSchema, dependencies=[Depends(AssetPermissions.CanViewAssets)])
async def get_assets_overview(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    filters = _build_filters(region_id, service_id, date_from, date_to)
    return AnalyticsResponseSchema(data=await service.overview(filters, current_user), meta=_meta(filters))
