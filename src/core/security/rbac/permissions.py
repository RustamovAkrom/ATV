from db.models.enums import UserRole


class Permissions:
    """
    Centralized permission registry for the entire application.
    All permissions must be defined here for consistency and validation.
    Format: "resource.action" (e.g., "asset.view", "user.delete")
    """

    # ======================== USERS & PROFILE ========================
    USERS_VIEW = "users.view"
    USERS_CREATE = "users.create"
    USERS_EDIT = "users.edit"
    USERS_DELETE = "users.delete"
    USERS_PASSWORD_RESET = "users.password_reset"  # Reset other user passwords
    USERS_BULK_EDIT = "users.bulk_edit"
    USERS_BULK_DELETE = "users.bulk_delete"

    # ======================== RBAC (Roles & Permissions) ========================
    ROLES_VIEW = "roles.view"
    ROLES_MANAGE = "roles.manage"  # Create, update, delete roles
    PERMISSIONS_MANAGE = "permissions.manage"  # Assign permissions to roles

    # ======================== AUDIT & SECURITY LOGS ========================
    AUDIT_VIEW = "audit.view"
    AUDIT_EXPORT = "audit.export"
    AUDIT_CLEANUP = "audit.cleanup"  # Only for SuperAdmin

    # ======================== SESSIONS ========================
    SESSIONS_VIEW = "sessions.view"
    SESSIONS_REVOKE = "sessions.revoke"
    SESSIONS_REVOKE_ALL = "sessions.revoke_all"

    # ======================== ASSETS & INVENTORY ========================
    ASSETS_VIEW = "assets.view"
    ASSETS_CREATE = "assets.create"
    ASSETS_UPDATE = "assets.update"
    ASSETS_DELETE = "assets.delete"
    ASSETS_ASSIGN = "assets.assign"  # Assign to users
    ASSETS_TRANSFER = "assets.transfer"  # Transfer ownership
    ASSETS_EXPORT = "assets.export"
    ASSETS_ARCHIVE = "assets.archive"

    # ======================== APPROVALS ========================
    APPROVALS_VIEW = "approvals.view"
    APPROVALS_CREATE = "approvals.create"
    APPROVALS_APPROVE = "approvals.approve"
    APPROVALS_REJECT = "approvals.reject"

    # ======================== REPAIRS & MAINTENANCE ========================
    REPAIRS_VIEW = "repairs.view"
    REPAIRS_CREATE = "repairs.create"
    REPAIRS_UPDATE = "repairs.update"
    REPAIRS_COMPLETE = "repairs.complete"
    REPAIRS_EXPORT = "repairs.export"

    # ======================== DOCUMENTS ========================
    DOCUMENTS_VIEW = "documents.view"
    DOCUMENTS_CREATE = "documents.create"
    DOCUMENTS_UPDATE = "documents.update"
    DOCUMENTS_DELETE = "documents.delete"
    DOCUMENTS_EXPORT = "documents.export"

    # ======================== ANALYTICS & REPORTING ========================
    ANALYTICS_VIEW = "analytics.view"
    ANALYTICS_DASHBOARD = "analytics.dashboard"
    ANALYTICS_EXPORT = "analytics.export"
    ANALYTICS_FORECAST = "analytics.forecast"

    # ======================== ORGANIZATION (Regions, Services) ========================
    ORG_REGIONS_VIEW = "org.regions.view"
    ORG_REGIONS_MANAGE = "org.regions.manage"
    ORG_SERVICES_VIEW = "org.services.view"
    ORG_SERVICES_MANAGE = "org.services.manage"
    ORG_RANKS_VIEW = "org.ranks.view"
    ORG_RANKS_MANAGE = "org.ranks.manage"

    # ======================== WAREHOUSE & INVENTORY ========================
    WAREHOUSE_VIEW = "warehouse.view"
    WAREHOUSE_MANAGE = "warehouse.manage"
    WAREHOUSE_EXPORT = "warehouse.export"

    # ======================== SYSTEM ========================
    SYSTEM_SETTINGS = "system.settings"
    SYSTEM_HEALTH = "system.health"
    SYSTEM_LOGS = "system.logs"

    @classmethod
    def all(cls) -> set[str]:
        """Returns all defined permissions as a set."""
        return {
            v
            for k, v in cls.__dict__.items()
            if isinstance(v, str) and not k.startswith("_") and "." in v
        }


# ======================== PERMISSION SETS FOR ROLES ========================

# Base permissions for all staff
BASE_STAFF = {
    Permissions.USERS_VIEW,
    Permissions.SESSIONS_VIEW,
    Permissions.SYSTEM_HEALTH,
}

# Moderator base permissions
MODERATOR_BASE = BASE_STAFF | {
    Permissions.ASSETS_VIEW,
    Permissions.REPAIRS_VIEW,
    Permissions.REPAIRS_CREATE,
    Permissions.ANALYTICS_VIEW,
}

# Admin base permissions
ADMIN_BASE = MODERATOR_BASE | {
    Permissions.USERS_CREATE,
    Permissions.USERS_EDIT,
    Permissions.USERS_PASSWORD_RESET,
    Permissions.SESSIONS_REVOKE,
    Permissions.ROLES_VIEW,
    Permissions.ASSETS_CREATE,
    Permissions.ASSETS_UPDATE,
    Permissions.ASSETS_DELETE,
    Permissions.ASSETS_EXPORT,
    Permissions.AUDIT_VIEW,
    Permissions.DOCUMENTS_VIEW,
    Permissions.DOCUMENTS_CREATE,
    Permissions.DOCUMENTS_UPDATE,
}

# Mapping of roles to their default permissions
ROLE_PERMISSIONS: dict[str, set[str]] = {
    # Supreme access - all permissions
    UserRole.SUPERADMIN.value: Permissions.all(),

    # Full operational control, but not system cleanup/audit cleanup
    UserRole.ADMIN.value: ADMIN_BASE | {
        Permissions.SYSTEM_SETTINGS,
        Permissions.PERMISSIONS_MANAGE,
        Permissions.APPROVALS_VIEW,
        Permissions.APPROVALS_APPROVE,
        Permissions.APPROVALS_REJECT,
    },

    # Region-specific admin (usually MODERATOR)
    UserRole.MODERATOR.value: MODERATOR_BASE | {
        Permissions.APPROVALS_VIEW,
        Permissions.APPROVALS_APPROVE,
        Permissions.REPAIRS_UPDATE,
        Permissions.REPAIRS_COMPLETE,
    },

    # Analyst / Officer
    UserRole.ANALYTIC.value: {
        Permissions.AUDIT_VIEW,
        Permissions.AUDIT_EXPORT,
        Permissions.USERS_VIEW,
        Permissions.ASSETS_VIEW,
        Permissions.ASSETS_EXPORT,
        Permissions.REPAIRS_VIEW,
        Permissions.REPAIRS_EXPORT,
        Permissions.ANALYTICS_VIEW,
        Permissions.ANALYTICS_EXPORT,
        Permissions.ANALYTICS_DASHBOARD,
        Permissions.SYSTEM_HEALTH,
        Permissions.DOCUMENTS_VIEW,
        Permissions.WAREHOUSE_VIEW,
    },

    # Region Admin - manages region-scoped operations
    UserRole.REGION_ADMIN.value: {
        Permissions.USERS_VIEW,
        Permissions.USERS_EDIT,
        Permissions.ASSETS_VIEW,
        Permissions.ASSETS_CREATE,
        Permissions.ASSETS_UPDATE,
        Permissions.ASSETS_ASSIGN,
        Permissions.APPROVALS_VIEW,
        Permissions.APPROVALS_APPROVE,
        Permissions.REPAIRS_VIEW,
        Permissions.REPAIRS_CREATE,
        Permissions.REPAIRS_UPDATE,
        Permissions.ANALYTICS_VIEW,
        Permissions.DOCUMENTS_VIEW,
        Permissions.WAREHOUSE_VIEW,
    },

    # Service Manager - manages service-scoped operations
    UserRole.SERVICE_MANAGER.value: {
        Permissions.ASSETS_VIEW,
        Permissions.ASSETS_CREATE,
        Permissions.ASSETS_UPDATE,
        Permissions.ASSETS_ASSIGN,
        Permissions.REPAIRS_VIEW,
        Permissions.REPAIRS_CREATE,
        Permissions.REPAIRS_UPDATE,
        Permissions.REPAIRS_COMPLETE,
        Permissions.APPROVALS_VIEW,
        Permissions.APPROVALS_CREATE,
        Permissions.APPROVALS_APPROVE,
        Permissions.ANALYTICS_VIEW,
        Permissions.DOCUMENTS_VIEW,
    },

    # Operator - basic operational access
    UserRole.OPERATOR.value: {
        Permissions.ASSETS_VIEW,
        Permissions.ASSETS_UPDATE,
        Permissions.REPAIRS_VIEW,
        Permissions.REPAIRS_CREATE,
        Permissions.APPROVALS_VIEW,
        Permissions.DOCUMENTS_VIEW,
        Permissions.ANALYTICS_VIEW,
    },

    # Approver - focus on approvals
    UserRole.APPROVER.value: {
        Permissions.APPROVALS_VIEW,
        Permissions.APPROVALS_APPROVE,
        Permissions.APPROVALS_REJECT,
        Permissions.ASSETS_VIEW,
        Permissions.REPAIRS_VIEW,
        Permissions.DOCUMENTS_VIEW,
    },

    # Auditor - read-only access to audit and analytics
    UserRole.AUDITOR.value: {
        Permissions.AUDIT_VIEW,
        Permissions.AUDIT_EXPORT,
        Permissions.ANALYTICS_VIEW,
        Permissions.ANALYTICS_EXPORT,
        Permissions.ANALYTICS_DASHBOARD,
        Permissions.USERS_VIEW,
        Permissions.ASSETS_VIEW,
        Permissions.REPAIRS_VIEW,
        Permissions.DOCUMENTS_VIEW,
        Permissions.SYSTEM_HEALTH,
        Permissions.SYSTEM_LOGS,
    },
}

