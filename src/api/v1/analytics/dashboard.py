from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies.analytics import get_dashboard_service
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.common import AnalyticsFilters, AnalyticsMetaSchema, AnalyticsResponseSchema
from schemas.auth import CurrentUserSchema
from services.dashboard.dashboard_service import DashboardService
from utils.helpers import utc_now

router = APIRouter(prefix="/analytics/dashboard", tags=["Analytics - Dashboard v2"])


@router.get("/", response_model=AnalyticsResponseSchema, dependencies=[Depends(AssetPermissions.CanViewAssets)])
async def get_dashboard(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
):
    filters = AnalyticsFilters(
        region_id=region_id, service_id=service_id, date_from=date_from, date_to=date_to
    )
    return AnalyticsResponseSchema(
        data=await service.get(filters, current_user),
        meta=AnalyticsMetaSchema(generated_at=utc_now(), filters=filters),
    )
