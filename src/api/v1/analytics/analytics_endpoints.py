from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies.analytics import (
    get_approval_analytics_domain_service,
    get_asset_analytics_domain_service,
    get_document_analytics_domain_service,
    get_report_service,
    get_repair_analytics_domain_service,
    get_transfer_analytics_domain_service,
    get_utilization_analytics_domain_service,
)
from core.security.auth.dependencies import get_current_user
from core.security.rbac import presets
from schemas.analytics.common import AnalyticsFilters, AnalyticsMetaSchema, AnalyticsResponseSchema
from schemas.auth import CurrentUserSchema
from services.analytics.approval_analytics_service import ApprovalAnalyticsDomainService
from services.analytics.asset_analytics_service import AssetAnalyticsService
from services.analytics.document_analytics_service import DocumentAnalyticsDomainService
from services.analytics.repair_analytics_service import RepairAnalyticsDomainService
from services.analytics.report_service import ReportService
from services.analytics.transfer_analytics_service import TransferAnalyticsDomainService
from services.analytics.utilization_analytics_service import UtilizationAnalyticsDomainService
from utils.helpers import utc_now

router = APIRouter(prefix="/analytics", tags=["Analytics - Intelligence"])


def _filters(
    region_id: UUID | None,
    service_id: UUID | None,
    date_from: date | None,
    date_to: date | None,
):
    return AnalyticsFilters(
        region_id=region_id, service_id=service_id, date_from=date_from, date_to=date_to
    )


def _resp(data: dict, filters: AnalyticsFilters):
    return AnalyticsResponseSchema(
        data=data, meta=AnalyticsMetaSchema(generated_at=utc_now(), filters=filters)
    )


@router.get("/overview", response_model=AnalyticsResponseSchema, dependencies=[presets.CanViewAssets])
async def overview(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    f = _filters(region_id, service_id, date_from, date_to)
    return _resp(await service.overview(f, current_user), f)


@router.get("/assets/distribution", response_model=AnalyticsResponseSchema, dependencies=[presets.CanViewAssets])
async def assets_distribution(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetAnalyticsService = Depends(get_asset_analytics_domain_service),
):
    f = _filters(region_id, service_id, date_from, date_to)
    return _resp(await service.distribution(f, current_user), f)


@router.get("/assets/lifecycle", response_model=AnalyticsResponseSchema, dependencies=[presets.CanViewAssets])
async def assets_lifecycle(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetAnalyticsService = Depends(get_asset_analytics_domain_service),
):
    f = _filters(region_id, service_id, date_from, date_to)
    return _resp(await service.lifecycle(f, current_user), f)


@router.get("/repairs", response_model=AnalyticsResponseSchema, dependencies=[presets.CanViewAssets])
async def repairs(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: RepairAnalyticsDomainService = Depends(get_repair_analytics_domain_service),
):
    f = _filters(region_id, service_id, date_from, date_to)
    return _resp(await service.get(f, current_user), f)


@router.get("/transfers", response_model=AnalyticsResponseSchema, dependencies=[presets.CanViewAssets])
async def transfers(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: TransferAnalyticsDomainService = Depends(get_transfer_analytics_domain_service),
):
    f = _filters(region_id, service_id, date_from, date_to)
    return _resp(await service.get(f, current_user), f)


@router.get("/approvals", response_model=AnalyticsResponseSchema, dependencies=[presets.CanViewApprovals])
async def approvals(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: ApprovalAnalyticsDomainService = Depends(get_approval_analytics_domain_service),
):
    f = _filters(region_id, service_id, date_from, date_to)
    return _resp(await service.get(f, current_user), f)


@router.get("/documents", response_model=AnalyticsResponseSchema, dependencies=[presets.CanViewAssets])
async def documents(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: DocumentAnalyticsDomainService = Depends(get_document_analytics_domain_service),
):
    f = _filters(region_id, service_id, date_from, date_to)
    return _resp(await service.get(f, current_user), f)


@router.get("/utilization", response_model=AnalyticsResponseSchema, dependencies=[presets.CanViewAssets])
async def utilization(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: UtilizationAnalyticsDomainService = Depends(get_utilization_analytics_domain_service),
):
    f = _filters(region_id, service_id, date_from, date_to)
    return _resp(await service.get(f, current_user), f)


@router.get("/report", response_model=AnalyticsResponseSchema, dependencies=[presets.CanViewAssets])
async def report(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    f = _filters(region_id, service_id, date_from, date_to)
    return _resp(await service.report(f, current_user), f)
