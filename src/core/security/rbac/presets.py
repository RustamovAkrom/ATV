from fastapi import Depends

from core.security.rbac.guards import require_permission, require_role
from core.security.rbac.permissions import Permissions
from db.models.enums import UserRole

# =================================================================
# ROLE-BASED PRESETS (Жесткие проверки по роли)
# =================================================================

class AdministrativPermissions:
    # Только для разработчика/главного админа
    IsSuperAdmin = require_role(UserRole.SUPERADMIN.value)

    # Для административного персонала (пропустит и супера)
    IsAdmin = require_role(UserRole.ADMIN.value)

    # Для модераторов
    IsModerator = require_role(UserRole.MODERATOR.value)

    # Любой сотрудник (не обычный юзер)
    IsStaff = require_role(
        UserRole.ADMIN.value, UserRole.MODERATOR.value, UserRole.ANALYTIC.value
    )

    IsAdminOrAnalytic = require_role(
        UserRole.ADMIN.value,
        UserRole.ANALYTIC.value,
    )

# =================================================================
# PERMISSION-BASED PRESETS (Гибкие проверки по правам)
# =================================================================
class UserPermissions:
    # --- Users Management ---
    CanViewUsers = require_permission(Permissions.USERS_VIEW)
    CanCreateUsers = require_permission(Permissions.USERS_CREATE)
    CanManageUsers = require_permission(Permissions.USERS_EDIT, Permissions.USERS_CREATE)

    CanDeleteUsers = require_permission(Permissions.USERS_DELETE)

class AuditPermissions:
    # --- Audit & Security ---
    CanViewAudit = require_permission(Permissions.AUDIT_VIEW)
    CanExportAudit = require_permission(Permissions.AUDIT_EXPORT)
    CanFullAuditControl = require_permission(Permissions.AUDIT_VIEW, Permissions.AUDIT_CLEANUP)

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
    CanViewExpenses = require_permission(Permissions.EXPENSES_READ)
    CanCreateExpenses = require_permission(Permissions.EXPENSES_CREATE)
    CanUpdateExpenses = require_permission(Permissions.EXPENSES_UPDATE)
    CanDeleteExpenses = require_permission(Permissions.EXPENSES_DELETE)
