from fastapi import APIRouter, Depends, Query, Request

from api.dependencies.analytics import (
    get_alert_analytics_service,
    get_analytics_alert_service,
)
from api.v1.analytics._utils import (
    enforce_rate_limit,
    parse_rate_limit,
    run_analytics_operation,
)
from core.cache.decorators import cached
from core.config import get_settings
from core.security.rbac import presets
from schemas.analytics.alerts import AlertOut
from services.analytics.alert_analytics_service import AlertAnalyticsService
from services.analytics.alert_service import AnalyticsAlertService

router = APIRouter(prefix="/analytics/alerts", tags=["Analytics - Alerts"])
settings = get_settings()
ANALYTICS_LIMIT, ANALYTICS_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS)


@router.get("/", response_model=list[AlertOut], dependencies=[presets.CanViewAssets])
@cached(ttl=120, tags=("analytics:alerts",))
async def get_alerts(
    request: Request,
    transfer_days: int | None = Query(default=None, ge=1, le=365),
    repair_days: int | None = Query(default=None, ge=1, le=365),
    repair_threshold: int | None = Query(default=None, ge=1, le=100),
    inactive_days: int | None = Query(default=None, ge=1, le=365),
    assignment_threshold: int | None = Query(default=None, ge=1, le=100),
    service: AlertAnalyticsService = Depends(get_alert_analytics_service),
):
    await enforce_rate_limit(
        request, "analytics:alerts", ANALYTICS_LIMIT, ANALYTICS_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.alerts",
        {
            "transfer_days": transfer_days,
            "repair_days": repair_days,
            "repair_threshold": repair_threshold,
            "inactive_days": inactive_days,
            "assignment_threshold": assignment_threshold,
        },
        lambda: service.get_alerts(
            transfer_days=transfer_days,
            repair_days=repair_days,
            repair_threshold=repair_threshold,
            inactive_days=inactive_days,
            assignment_threshold=assignment_threshold,
        ),
        lambda: [],
    )


@router.post(
    "/dispatch",
    dependencies=[presets.CanManageApprovals],
)
async def dispatch_analytics_alerts(
    request: Request,
    service: AnalyticsAlertService = Depends(get_analytics_alert_service),
):
    await enforce_rate_limit(
        request, "analytics:alerts:dispatch", ANALYTICS_LIMIT, ANALYTICS_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.alerts.dispatch",
        {},
        lambda: service.dispatch(),
        lambda: 0,
    )
