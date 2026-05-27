from core.security.rbac.guards import require_permission, require_role
from core.security.rbac.permissions import Permissions
from db.models.enums import UserRole

# =================================================================
# ROLE-BASED PRESETS (Жесткие проверки по роли)
# =================================================================


class AdministrativePermissions:
    # Только для разработчика/главного админа
    IsSuperAdmin = require_role(UserRole.SUPERADMIN.value)

    # Для административного персонала (пропустит и супера)
    IsAdmin = require_role(UserRole.ADMIN.value)

    # Любой сотрудник
    IsStaff = require_role(
        UserRole.ADMIN.value,
        UserRole.ANALYST.value,
        UserRole.OPERATOR.value,
        UserRole.APPROVER.value,
    )

    IsAdminOrAnalyst = require_role(
        UserRole.ADMIN.value,
        UserRole.ANALYST.value,
    )


# =================================================================
# PERMISSION-BASED PRESETS (Гибкие проверки по правам)
# =================================================================
class UserPermissions:
    # --- Users Management ---
    CanViewUsers = require_permission(Permissions.USERS_VIEW)
    CanCreateUsers = require_permission(Permissions.USERS_CREATE)
    CanManageUsers = require_permission(
        Permissions.USERS_EDIT, Permissions.USERS_CREATE
    )

    CanDeleteUsers = require_permission(Permissions.USERS_DELETE)


class AuditPermissions:
    # --- Audit & Security ---
    CanViewAudit = require_permission(Permissions.AUDIT_VIEW)
    CanExportAudit = require_permission(Permissions.AUDIT_EXPORT)
    CanFullAuditControl = require_permission(
        Permissions.AUDIT_VIEW, Permissions.AUDIT_CLEANUP
    )


class RBACPermissions:
    # --- RBAC ---
    CanManageRoles = require_permission(Permissions.ROLES_MANAGE)


class UserSessionPermissions:
    # --- Sessions ---
    CanViewSessions = require_permission(Permissions.SESSIONS_VIEW)
    CanRevokeSessions = require_permission(Permissions.SESSIONS_REVOKE)


class AssetPermissions:
    # --- Assets ---
    CanViewAssets = require_permission(Permissions.ASSETS_VIEW)
    CanCreateAssets = require_permission(Permissions.ASSETS_CREATE)
    CanUpdateAssets = require_permission(Permissions.ASSETS_UPDATE)
    CanDeleteAssets = require_permission(Permissions.ASSETS_DELETE)
    CanExportAssets = require_permission(Permissions.ASSETS_EXPORT)


class AssetAssignmentPermissions:
    CanViewAssignments = require_permission(Permissions.ASSETS_ASSIGNMENTS_VIEW)
    CanAssignAssets = require_permission(Permissions.ASSETS_ASSIGN)
    CanUnassignAssets = require_permission(Permissions.ASSETS_UNASSIGN)
    CanManageAssignments = require_permission(
        Permissions.ASSETS_ASSIGN,
        Permissions.ASSETS_UNASSIGN,
        Permissions.ASSETS_ASSIGNMENTS_VIEW,
    )


class RepairsPermissions:
    CanViewRepairs = require_permission(Permissions.REPAIRS_VIEW)
    CanCreateRepairs = require_permission(Permissions.REPAIRS_CREATE)
    CanUpdateRepairs = require_permission(Permissions.REPAIRS_UPDATE)
    CanCompleteRepairs = require_permission(Permissions.REPAIRS_COMPLETE)
    CanExportRepairs = require_permission(Permissions.REPAIRS_EXPORT)


class ModelsPermissions:
    CanViewModels = require_permission(Permissions.MODELS_VIEW)
    CanCreateModels = require_permission(Permissions.MODELS_CREATE)
    CanUpdateModels = require_permission(Permissions.MODELS_UPDATE)
    CanDeleteModels = require_permission(Permissions.MODELS_DELETE)
    CanExportModels = require_permission(Permissions.MODELS_EXPORT)


class MaintenancesPermissions:
    CanViewMaintenances = require_permission(Permissions.MAINTENANCE_VIEW)
    CanCreateMaintenances = require_permission(Permissions.MAINTENANCE_CREATE)
    CanUpdateMaintenances = require_permission(Permissions.MAINTENANCE_UPDATE)
    CanDeleteMaintenances = require_permission(Permissions.MAINTENANCE_DELETE)
    CanExportMaintenances = require_permission(Permissions.MAINTENANCE_EXPORT)


class ImagesPermissions:
    CanViewImages = require_permission(Permissions.IMAGES_VIEW)
    CanUploadImages = require_permission(Permissions.IMAGES_UPLOAD)
    CanUpdateImages = require_permission(Permissions.IMAGES_UPDATE)
    CanDeleteImages = require_permission(Permissions.IMAGES_DELETE)


class ClassesPermissions:
    CanViewClasses = require_permission(Permissions.CLASSES_VIEW)
    CanCreateClasses = require_permission(Permissions.CLASSES_CREATE)
    CanUpdateClasses = require_permission(Permissions.CLASSES_UPDATE)
    CanDeleteClasses = require_permission(Permissions.CLASSES_DELETE)
    CanExportClasses = require_permission(Permissions.CLASSES_EXPORT)


class CategoriesPermissions:
    CanViewCategories = require_permission(Permissions.CATEGORIES_VIEW)
    CanCreateCategories = require_permission(Permissions.CATEGORIES_CREATE)
    CanUpdateCategories = require_permission(Permissions.CATEGORIES_UPDATE)
    CanDeleteCategories = require_permission(Permissions.CATEGORIES_DELETE)
    CanExportCategories = require_permission(Permissions.CATEGORIES_EXPORT)


class DocumentsPermissions:
    CanViewDocuments = require_permission(Permissions.DOCUMENTS_VIEW)
    CanCreateDocuments = require_permission(Permissions.DOCUMENTS_CREATE)
    CanUpdateDocuments = require_permission(Permissions.DOCUMENTS_UPDATE)
    CanDeleteDocuments = require_permission(Permissions.DOCUMENTS_DELETE)
    CanExportDocuments = require_permission(Permissions.DOCUMENTS_EXPORT)


class AssetApprovalPermissions:
    # --- Approvals ---
    CanViewApprovals = require_permission(Permissions.APPROVALS_VIEW)
    CanCreateApprovals = require_permission(Permissions.APPROVALS_CREATE)
    CanApproveApprovals = require_permission(Permissions.APPROVALS_APPROVE)
    CanRejectApprovals = require_permission(Permissions.APPROVALS_REJECT)
    CanManageApprovals = require_permission(
        Permissions.APPROVALS_APPROVE,
        Permissions.APPROVALS_REJECT,
    )


class WarehousePermission:
    CanViewWarehouses = require_permission(Permissions.WAREHOUSE_VIEW)
    CanCreateWarehouses = require_permission(Permissions.WAREHOUSE_CREATE)
    CanUpdateWarehouses = require_permission(Permissions.WAREHOUSE_UPDATE)
    CanDeleteWarehouses = require_permission(Permissions.WAREHOUSE_DELETE)
    CanExportWarehouses = require_permission(Permissions.WAREHOUSE_EXPORT)


class ManufacturePermission:
    CanViewManufacture = require_permission(Permissions.MANUFACTURE_VIEW)
    CanCreateManufacture = require_permission(Permissions.MANUFACTURE_CREATE)
    CanUpdateManufacture = require_permission(Permissions.MANUFACTURE_UPDATE)
    CanDeleteManufacture = require_permission(Permissions.MANUFACTURE_DELETE)
    CanExportManufacture = require_permission(Permissions.MANUFACTURE_EXPORT)


class ServicePermissions:
    CanViewServices = require_permission(Permissions.ORG_SERVICES_VIEW)
    CanCreateServices = require_permission(Permissions.ORG_SERVICES_CREATE)
    CanUpdateServices = require_permission(Permissions.ORG_SERVICES_UPDATE)
    CanDeleteServices = require_permission(Permissions.ORG_SERVICES_DELETE)


class RegionPermissions:
    CanViewRegions = require_permission(Permissions.ORG_REGIONS_VIEW)
    CanCreateRegions = require_permission(Permissions.ORG_REGIONS_CREATE)
    CanUpdateRegions = require_permission(Permissions.ORG_REGIONS_UPDATE)
    CanDeleteRegions = require_permission(Permissions.ORG_REGIONS_DELETE)


class SystemPermission:
    # --- System ---
    CanViewSystemHealth = require_permission(Permissions.SYSTEM_HEALTH)


class ExpensePermission:
    # Expenses
    CanViewExpenses = require_permission(Permissions.EXPENSES_VIEW)
    CanCreateExpenses = require_permission(Permissions.EXPENSES_CREATE)
    CanUpdateExpenses = require_permission(Permissions.EXPENSES_UPDATE)
    CanDeleteExpenses = require_permission(Permissions.EXPENSES_DELETE)
