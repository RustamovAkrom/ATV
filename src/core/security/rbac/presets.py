from collections.abc import Awaitable, Callable

from core.security.rbac.guards import require_permission, require_role
from core.security.rbac.permissions import Permissions
from db.models.enums import UserRole
from schemas.auth import CurrentUserSchema

# =================================================================
# ROLE-BASED PRESETS (Жесткие проверки по роли)
# =================================================================
PermissionDependency = Callable[..., Awaitable[CurrentUserSchema]]


class AdministrativePermissions:
    # Только для разработчика/главного админа
    IsSuperAdmin: PermissionDependency = require_role(UserRole.SUPERADMIN.value)

    # Для административного персонала (пропустит и супера)
    IsAdmin: PermissionDependency = require_role(UserRole.ADMIN.value)

    # Любой сотрудник
    IsStaff: PermissionDependency = require_role(
        UserRole.ADMIN.value,
        UserRole.ANALYST.value,
        UserRole.OPERATOR.value,
        UserRole.APPROVER.value,
    )

    IsAdminOrAnalyst: PermissionDependency = require_role(
        UserRole.ADMIN.value,
        UserRole.ANALYST.value,
    )


# =================================================================
# PERMISSION-BASED PRESETS (Гибкие проверки по правам)
# =================================================================
class UserPermissions:
    # --- Users Management ---
    CanViewUsers: PermissionDependency = require_permission(Permissions.USERS_VIEW)
    CanCreateUsers: PermissionDependency = require_permission(Permissions.USERS_CREATE)
    CanManageUsers: PermissionDependency = require_permission(
        Permissions.USERS_EDIT, Permissions.USERS_CREATE
    )
    CanDeleteUsers: PermissionDependency = require_permission(Permissions.USERS_DELETE)


class AuditPermissions:
    # --- Audit & Security ---
    CanViewAudit: PermissionDependency = require_permission(Permissions.AUDIT_VIEW)
    CanExportAudit: PermissionDependency = require_permission(Permissions.AUDIT_EXPORT)
    CanFullAuditControl: PermissionDependency = require_permission(
        Permissions.AUDIT_VIEW, Permissions.AUDIT_CLEANUP
    )


class RBACPermissions:
    CanManageRoles: PermissionDependency = require_permission(Permissions.ROLES_MANAGE)


class UserSessionPermissions:
    CanViewSessions: PermissionDependency = require_permission(
        Permissions.SESSIONS_VIEW
    )
    CanRevokeSessions: PermissionDependency = require_permission(
        Permissions.SESSIONS_REVOKE
    )


class AssetPermissions:
    CanViewAssets: PermissionDependency = require_permission(Permissions.ASSETS_VIEW)
    CanCreateAssets: PermissionDependency = require_permission(
        Permissions.ASSETS_CREATE
    )
    CanUpdateAssets: PermissionDependency = require_permission(
        Permissions.ASSETS_UPDATE
    )
    CanDeleteAssets: PermissionDependency = require_permission(
        Permissions.ASSETS_DELETE
    )
    CanExportAssets: PermissionDependency = require_permission(
        Permissions.ASSETS_EXPORT
    )


class AssetAssignmentPermissions:
    CanViewAssignments: PermissionDependency = require_permission(
        Permissions.ASSETS_ASSIGNMENTS_VIEW
    )
    CanAssignAssets: PermissionDependency = require_permission(
        Permissions.ASSETS_ASSIGN
    )
    CanUnassignAssets: PermissionDependency = require_permission(
        Permissions.ASSETS_UNASSIGN
    )
    CanManageAssignments: PermissionDependency = require_permission(
        Permissions.ASSETS_ASSIGN,
        Permissions.ASSETS_UNASSIGN,
        Permissions.ASSETS_ASSIGNMENTS_VIEW,
    )


class RepairsPermissions:
    CanViewRepairs: PermissionDependency = require_permission(Permissions.REPAIRS_VIEW)
    CanCreateRepairs: PermissionDependency = require_permission(
        Permissions.REPAIRS_CREATE
    )
    CanUpdateRepairs: PermissionDependency = require_permission(
        Permissions.REPAIRS_UPDATE
    )
    CanCompleteRepairs: PermissionDependency = require_permission(
        Permissions.REPAIRS_COMPLETE
    )
    CanExportRepairs: PermissionDependency = require_permission(
        Permissions.REPAIRS_EXPORT
    )


class ModelsPermissions:
    CanViewModels: PermissionDependency = require_permission(Permissions.MODELS_VIEW)
    CanCreateModels: PermissionDependency = require_permission(
        Permissions.MODELS_CREATE
    )
    CanUpdateModels: PermissionDependency = require_permission(
        Permissions.MODELS_UPDATE
    )
    CanDeleteModels: PermissionDependency = require_permission(
        Permissions.MODELS_DELETE
    )
    CanExportModels: PermissionDependency = require_permission(
        Permissions.MODELS_EXPORT
    )


class MaintenancesPermissions:
    CanViewMaintenances: PermissionDependency = require_permission(
        Permissions.MAINTENANCE_VIEW
    )
    CanCreateMaintenances: PermissionDependency = require_permission(
        Permissions.MAINTENANCE_CREATE
    )
    CanUpdateMaintenances: PermissionDependency = require_permission(
        Permissions.MAINTENANCE_UPDATE
    )
    CanDeleteMaintenances: PermissionDependency = require_permission(
        Permissions.MAINTENANCE_DELETE
    )
    CanExportMaintenances: PermissionDependency = require_permission(
        Permissions.MAINTENANCE_EXPORT
    )


class ImagesPermissions:
    CanViewImages: PermissionDependency = require_permission(Permissions.IMAGES_VIEW)
    CanUploadImages: PermissionDependency = require_permission(
        Permissions.IMAGES_UPLOAD
    )
    CanUpdateImages: PermissionDependency = require_permission(
        Permissions.IMAGES_UPDATE
    )
    CanDeleteImages: PermissionDependency = require_permission(
        Permissions.IMAGES_DELETE
    )


class ClassesPermissions:
    CanViewClasses: PermissionDependency = require_permission(Permissions.CLASSES_VIEW)
    CanCreateClasses: PermissionDependency = require_permission(
        Permissions.CLASSES_CREATE
    )
    CanUpdateClasses: PermissionDependency = require_permission(
        Permissions.CLASSES_UPDATE
    )
    CanDeleteClasses: PermissionDependency = require_permission(
        Permissions.CLASSES_DELETE
    )
    CanExportClasses: PermissionDependency = require_permission(
        Permissions.CLASSES_EXPORT
    )


class CategoriesPermissions:
    CanViewCategories: PermissionDependency = require_permission(
        Permissions.CATEGORIES_VIEW
    )
    CanCreateCategories: PermissionDependency = require_permission(
        Permissions.CATEGORIES_CREATE
    )
    CanUpdateCategories: PermissionDependency = require_permission(
        Permissions.CATEGORIES_UPDATE
    )
    CanDeleteCategories: PermissionDependency = require_permission(
        Permissions.CATEGORIES_DELETE
    )
    CanExportCategories: PermissionDependency = require_permission(
        Permissions.CATEGORIES_EXPORT
    )


class DocumentsPermissions:
    CanViewDocuments: PermissionDependency = require_permission(
        Permissions.DOCUMENTS_VIEW
    )
    CanCreateDocuments: PermissionDependency = require_permission(
        Permissions.DOCUMENTS_CREATE
    )
    CanUpdateDocuments: PermissionDependency = require_permission(
        Permissions.DOCUMENTS_UPDATE
    )
    CanDeleteDocuments: PermissionDependency = require_permission(
        Permissions.DOCUMENTS_DELETE
    )
    CanExportDocuments: PermissionDependency = require_permission(
        Permissions.DOCUMENTS_EXPORT
    )


class AssetApprovalPermissions:
    # --- Approvals ---
    CanViewApprovals: PermissionDependency = require_permission(
        Permissions.APPROVALS_VIEW
    )
    CanCreateApprovals: PermissionDependency = require_permission(
        Permissions.APPROVALS_CREATE
    )
    CanApproveApprovals: PermissionDependency = require_permission(
        Permissions.APPROVALS_APPROVE
    )
    CanRejectApprovals: PermissionDependency = require_permission(
        Permissions.APPROVALS_REJECT
    )
    CanManageApprovals: PermissionDependency = require_permission(
        Permissions.APPROVALS_APPROVE,
        Permissions.APPROVALS_REJECT,
    )


class WarehousePermission:
    CanViewWarehouses: PermissionDependency = require_permission(
        Permissions.WAREHOUSE_VIEW
    )
    CanCreateWarehouses: PermissionDependency = require_permission(
        Permissions.WAREHOUSE_CREATE
    )
    CanUpdateWarehouses: PermissionDependency = require_permission(
        Permissions.WAREHOUSE_UPDATE
    )
    CanDeleteWarehouses: PermissionDependency = require_permission(
        Permissions.WAREHOUSE_DELETE
    )
    CanExportWarehouses: PermissionDependency = require_permission(
        Permissions.WAREHOUSE_EXPORT
    )


class ManufacturePermission:
    CanViewManufacture: PermissionDependency = require_permission(
        Permissions.MANUFACTURE_VIEW
    )
    CanCreateManufacture: PermissionDependency = require_permission(
        Permissions.MANUFACTURE_CREATE
    )
    CanUpdateManufacture: PermissionDependency = require_permission(
        Permissions.MANUFACTURE_UPDATE
    )
    CanDeleteManufacture: PermissionDependency = require_permission(
        Permissions.MANUFACTURE_DELETE
    )
    CanExportManufacture: PermissionDependency = require_permission(
        Permissions.MANUFACTURE_EXPORT
    )


class ServicePermissions:
    CanViewServices: PermissionDependency = require_permission(
        Permissions.ORG_SERVICES_VIEW
    )
    CanCreateServices: PermissionDependency = require_permission(
        Permissions.ORG_SERVICES_CREATE
    )
    CanUpdateServices: PermissionDependency = require_permission(
        Permissions.ORG_SERVICES_UPDATE
    )
    CanDeleteServices: PermissionDependency = require_permission(
        Permissions.ORG_SERVICES_DELETE
    )


class RegionPermissions:
    CanViewRegions: PermissionDependency = require_permission(
        Permissions.ORG_REGIONS_VIEW
    )
    CanCreateRegions: PermissionDependency = require_permission(
        Permissions.ORG_REGIONS_CREATE
    )
    CanUpdateRegions: PermissionDependency = require_permission(
        Permissions.ORG_REGIONS_UPDATE
    )
    CanDeleteRegions: PermissionDependency = require_permission(
        Permissions.ORG_REGIONS_DELETE
    )


class SystemPermission:
    # --- System ---
    CanViewSystemHealth: PermissionDependency = require_permission(
        Permissions.SYSTEM_HEALTH
    )


class ExpensePermission:
    # Expenses
    CanViewExpenses: PermissionDependency = require_permission(
        Permissions.EXPENSES_VIEW
    )
    CanCreateExpenses: PermissionDependency = require_permission(
        Permissions.EXPENSES_CREATE
    )
    CanUpdateExpenses: PermissionDependency = require_permission(
        Permissions.EXPENSES_UPDATE
    )
    CanDeleteExpenses: PermissionDependency = require_permission(
        Permissions.EXPENSES_DELETE
    )
