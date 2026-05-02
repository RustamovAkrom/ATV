from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies.analytics import get_report_service
from core.security.auth.dependencies import get_current_user
from core.security.rbac import presets
from schemas.analytics.common import AnalyticsFilters, AnalyticsMetaSchema, AnalyticsResponseSchema
from schemas.auth import CurrentUserSchema
from services.analytics.report_service import ReportService
from utils.helpers import utc_now

router = APIRouter(prefix="/analytics/reports", tags=["Analytics - Reports"])


@router.get("/", response_model=AnalyticsResponseSchema, dependencies=[presets.CanViewAssets])
async def get_report(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    filters = AnalyticsFilters(
        region_id=region_id, service_id=service_id, date_from=date_from, date_to=date_to
    )
    return AnalyticsResponseSchema(
        data=await service.report(filters, current_user),
        meta=AnalyticsMetaSchema(generated_at=utc_now(), filters=filters),
    )
