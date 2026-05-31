from fastapi import FastAPI
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from core.admin.auth import AdminAuth
from core.admin.views.assets import (
    AssetAdmin,
    AssetAssignmentAdmin,
    AssetCategoryAdmin,
    AssetClassAdmin,
    AssetHistoryAdmin,
    AssetImageAdmin,
    AssetMaintenanceAdmin,
    AssetModelAdmin,
    AssetTransferAdmin,
    ManufacturerAdmin,
    WarehouseAdmin,
)
from core.admin.views.assets.approvals import ApprovalRequestAdmin
from core.admin.views.assets.documents import DocumentAdmin, DocumentFileAdmin
from core.admin.views.assets.misc import (
    AuditLogAdmin,
    NotificationAdmin,
    RefreshTokenAdmin,
    SystemConfigAdmin,
)
from core.admin.views.assets.org import RegionAdmin, ServiceAdmin
from core.admin.views.assets.repairs import RepairAdmin, RepairPartAdmin
from core.admin.views.users import PermissionAdmin, RoleAdmin, UserAdmin
from core.config import Settings
from core.database.db_sync import get_db_sync_engine


def setup_admin(app: FastAPI, settings: Settings):
    engine = get_db_sync_engine()
    authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)

    # Добавляем SessionMiddleware отдельно (правильный способ)
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

    # Connect custom templates directory
    admin = Admin(
        app,
        engine,
        title="IIV ATV Admin Panel",
        base_url="/admin",
        authentication_backend=authentication_backend,
        templates_dir="src/templates",
    )

    # Users
    admin.add_view(UserAdmin)
    admin.add_view(RoleAdmin)
    admin.add_view(PermissionAdmin)

    # Assets
    admin.add_view(AssetAdmin)
    admin.add_view(AssetAssignmentAdmin)
    admin.add_view(AssetCategoryAdmin)
    admin.add_view(AssetClassAdmin)
    admin.add_view(AssetHistoryAdmin)
    admin.add_view(AssetModelAdmin)
    admin.add_view(AssetTransferAdmin)
    admin.add_view(ManufacturerAdmin)
    admin.add_view(WarehouseAdmin)
    admin.add_view(AssetMaintenanceAdmin)

    # Asset Images
    admin.add_view(AssetImageAdmin)

    # Documents
    admin.add_view(DocumentAdmin)
    admin.add_view(DocumentFileAdmin)

    # Org
    admin.add_view(RegionAdmin)
    admin.add_view(ServiceAdmin)

    # Repairs
    admin.add_view(RepairAdmin)
    admin.add_view(RepairPartAdmin)

    # Misc
    admin.add_view(AuditLogAdmin)
    admin.add_view(NotificationAdmin)
    admin.add_view(RefreshTokenAdmin)
    admin.add_view(SystemConfigAdmin)
    admin.add_view(ApprovalRequestAdmin)

    return admin
