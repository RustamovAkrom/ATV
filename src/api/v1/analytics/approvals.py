from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies.analytics import get_approval_analytics_domain_service
from core.security.auth.dependencies import get_current_user
from core.security.rbac import presets
from schemas.analytics.common import AnalyticsFilters, AnalyticsMetaSchema, AnalyticsResponseSchema
from schemas.auth import CurrentUserSchema
from services.analytics.approval_analytics_service import ApprovalAnalyticsDomainService
from utils.helpers import utc_now

router = APIRouter(prefix="/analytics/approvals", tags=["Analytics - Approvals"])


@router.get("/", response_model=AnalyticsResponseSchema, dependencies=[presets.CanViewApprovals])
async def get_approvals(
    region_id: UUID | None = Query(default=None),
    service_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: ApprovalAnalyticsDomainService = Depends(get_approval_analytics_domain_service),
):
    filters = AnalyticsFilters(
        region_id=region_id, service_id=service_id, date_from=date_from, date_to=date_to
    )
    return AnalyticsResponseSchema(
        data=await service.get(filters, current_user),
        meta=AnalyticsMetaSchema(generated_at=utc_now(), filters=filters),
    )
