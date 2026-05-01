from fastapi import APIRouter

from api.v1.analytics.alerts import router as alert_analytics_router
from api.v1.analytics.asset_history import router as asset_history_router
from api.v1.analytics.assignment_analytics import router as assignment_analytics_router
from api.v1.analytics.costs import router as cost_analytics_router
from api.v1.analytics.dashboard.router import router as analytics_dashboard_router
from api.v1.analytics.forecast import router as forecast_analytics_router
from api.v1.analytics.regions import router as region_analytics_router
from api.v1.analytics.top import router as top_analytics_router
from api.v1.analytics.transfer_analytics import router as transfer_analytics_router
from api.v1.analytics.trends import router as trend_analytics_router
from api.v1.approvals import router as approvals_router
from api.v1.assets.asset import router as assets_router
from api.v1.assets.asset_categories import router as asset_category_router
from api.v1.assets.asset_classes import router as asset_classes_router
from api.v1.assets.asset_model import router as asset_model_router
from api.v1.assets.manufacturer import router as manufacturer_router
from api.v1.audit.audit import router as audit_log_router
from api.v1.audit.audit_stream import router as audit_stream_router
from api.v1.auth.auth import router as auth_router
from api.v1.auth.sessions import router as sessions_router
from api.v1.rbac.rbac import router as rbac_router
from api.v1.users.security import router as security_router
from api.v1.users.user import router as users_router
from api.v1.notifications import router as notifications_router
from api.v1.assets.asset_documents import router as documents_router
from api.v1.assets.asset_repairs import router as asset_repairs_router
from api.v1.assets.asset_warehouse import router as asset_warehouse_router
from api.v1.approvals.requests import router as approval_requests_router

router = APIRouter()

# Auth & Users
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(security_router)
router.include_router(sessions_router)
router.include_router(rbac_router)

# User Notifications
router.include_router(notifications_router)

# Asset Domain (WRITE)
router.include_router(approvals_router)
router.include_router(assets_router)
router.include_router(asset_repairs_router)
router.include_router(asset_warehouse_router)

# Asset approval requests
router.include_router(approval_requests_router)

# Document Management
router.include_router(documents_router, prefix="/documents", tags=["Documents"])

# Reference Data
router.include_router(asset_category_router)
router.include_router(manufacturer_router)
router.include_router(asset_model_router)
router.include_router(asset_classes_router)

# Analytics (READ) - CQRS Read Layer
# router.include_router(asset_history_router)
# router.include_router(assignment_analytics_router)
# router.include_router(transfer_analytics_router)
# router.include_router(region_analytics_router)
# router.include_router(top_analytics_router)
# router.include_router(cost_analytics_router)
# router.include_router(trend_analytics_router)
# router.include_router(forecast_analytics_router)
# router.include_router(alert_analytics_router)
# router.include_router(analytics_dashboard_router)

# System Audit
router.include_router(audit_log_router)
router.include_router(audit_stream_router)
