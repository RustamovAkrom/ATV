from fastapi import APIRouter

from api.v1.analytics.alerts import router as alert_analytics_router
from api.v1.analytics.asset_history import router as asset_history_analytics_router
from api.v1.analytics.assets import router as assets_analytics_router
from api.v1.analytics.assignment_analytics import router as assignment_analytics_router
from api.v1.analytics.costs import router as costs_analytics_router
from api.v1.analytics.dashboard import router as dashboard_analytics_router
from api.v1.analytics.forecast import router as forecast_analytics_router
from api.v1.analytics.regions import router as regions_analytics_router
from api.v1.analytics.top import router as top_analytics_router
from api.v1.analytics.transfer_analytics import router as transfer_analytics_router
from api.v1.analytics.trends import router as trends_analytics_router
from api.v1.approvals import router as approvals_router
from api.v1.approvals.requests import router as approval_requests_router
from api.v1.assets.asset import router as assets_router
from api.v1.assets.asset_categories import router as asset_category_router
from api.v1.assets.asset_classes import router as asset_classes_router
from api.v1.assets.asset_documents import router as documents_router
from api.v1.assets.asset_images import router as asset_image_router
from api.v1.assets.asset_maintenances import router as asset_maintenances_router
from api.v1.assets.asset_model import router as asset_model_router
from api.v1.assets.asset_repairs import router as asset_repairs_router
from api.v1.assets.expenses import router as expenses_router
from api.v1.assets.manufacturer import router as manufacturer_router
from api.v1.assets.warehouses import router as warehouse_router
from api.v1.audit.audit import router as audit_log_router
from api.v1.audit.audit_stream import router as audit_stream_router
from api.v1.auth.auth import router as auth_router
from api.v1.auth.sessions import router as sessions_router
from api.v1.notifications import router as notifications_router
from api.v1.organization.regions import router as regions_router
from api.v1.organization.services import router as services_router
from api.v1.rbac.rbac import router as rbac_router
from api.v1.users.security import router as security_router
from api.v1.users.user import router as users_router
from api.v1.assets.asset_assignments import router as asset_assignments_router


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
router.include_router(asset_maintenances_router)

# Asset Assignments
router.include_router(asset_assignments_router)

# Asset Images
router.include_router(asset_image_router)

# Warehouse
router.include_router(warehouse_router)

# Asset approval requests
router.include_router(approval_requests_router)

# Document Management
router.include_router(documents_router)

# Reference Data
router.include_router(asset_category_router)
router.include_router(manufacturer_router)
router.include_router(asset_model_router)
router.include_router(asset_classes_router)

# Organization Management
router.include_router(regions_router)
router.include_router(services_router)

# Financial Management
router.include_router(expenses_router)

# Analytics (READ) - CQRS Read Layer
router.include_router(assets_analytics_router)
router.include_router(alert_analytics_router)
router.include_router(assignment_analytics_router)
router.include_router(asset_history_analytics_router)
router.include_router(costs_analytics_router)
router.include_router(dashboard_analytics_router)
router.include_router(forecast_analytics_router)
router.include_router(regions_analytics_router)
router.include_router(top_analytics_router)
router.include_router(transfer_analytics_router)
router.include_router(trends_analytics_router)

# System Audit
router.include_router(audit_log_router)
router.include_router(audit_stream_router)
