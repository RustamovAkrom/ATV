from sqladmin import Admin
from fastapi import FastAPI
from core.database.db_sync import get_db_sync_engine

from core.admin.views.users import UserAdmin, PermissionAdmin, RoleAdmin
from core.admin.views.assets import (
    AssetAdmin,
    AssetAssignmentAdmin,
    AssetCategoryAdmin,
    AssetClassAdmin,
    AssetHistoryAdmin,
    AssetModelAdmin,
    AssetTransferAdmin,
    ManufacturerAdmin,
    WarehouseAdmin,
)
from core.admin.views.assets.documents import DocumentAdmin, DocumentFileAdmin
from core.admin.views.assets.org import RankAdmin, RegionAdmin, ServiceAdmin
from core.admin.views.assets.repairs import RepairAdmin, RepairPartAdmin
from core.admin.views.assets.misc import AuditLogAdmin, NotificationAdmin, RefreshTokenAdmin, SystemConfigAdmin
from core.admin.views.assets.approvals import ApprovalRequestAdmin
from core.admin.views.assets.dashboard import DashboardView
from core.admin.auth import AdminAuth

from core.config import Settings


def setup_admin(app: FastAPI, settings: Settings):
    engine = get_db_sync_engine()
    authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    admin = Admin(
        app,
        engine,
        title="IIB ATV Admin Panel",
        base_url="/admin",
        authentication_backend=authentication_backend,
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

    # Documents
    admin.add_view(DocumentAdmin)
    admin.add_view(DocumentFileAdmin)

    # Org
    admin.add_view(RankAdmin)
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

    # Dashboard
    admin.add_view(DashboardView)

    return admin
