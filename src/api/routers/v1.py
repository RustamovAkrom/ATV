from fastapi import APIRouter

from api.v1.analytics.alerts import router as alert_analytics_router
from api.v1.analytics.analytics_endpoints import router as intelligence_analytics_router
from api.v1.analytics.approvals import router as approvals_analytics_v2_router
from api.v1.analytics.assets import router as assets_analytics_v2_router
from api.v1.analytics.dashboard.router import router as dashboard_v2_router
from api.v1.analytics.documents import router as documents_analytics_v2_router
from api.v1.analytics.repairs import router as repairs_analytics_v2_router
from api.v1.analytics.reports import router as reports_analytics_v2_router
from api.v1.analytics.transfers import router as transfers_analytics_v2_router
from api.v1.analytics.utilization import router as utilization_analytics_v2_router
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
router.include_router(intelligence_analytics_router)
router.include_router(alert_analytics_router)
router.include_router(assets_analytics_v2_router)
router.include_router(repairs_analytics_v2_router)
router.include_router(transfers_analytics_v2_router)
router.include_router(approvals_analytics_v2_router)
router.include_router(documents_analytics_v2_router)
router.include_router(utilization_analytics_v2_router)
router.include_router(dashboard_v2_router)
router.include_router(reports_analytics_v2_router)

# System Audit
router.include_router(audit_log_router)
router.include_router(audit_stream_router)
