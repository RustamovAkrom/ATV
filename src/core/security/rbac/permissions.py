from __future__ import annotations

from db.models.enums import UserRole


def _set(*permissions: str) -> frozenset[str]:
    return frozenset(permissions)


class Permissions:
    """
    Centralized permission registry for the whole application.

    Convention:
        <resource>.<action>

    Examples:
        users.view
        users.create
        assets.transfer
        audit.export
    """

    # ======================== USERS & PROFILE ========================
    USERS_VIEW = "users.view"
    USERS_CREATE = "users.create"
    USERS_EDIT = "users.edit"
    USERS_DELETE = "users.delete"
    USERS_PASSWORD_RESET = "users.password_reset"
    USERS_BULK_EDIT = "users.bulk_edit"
    USERS_BULK_DELETE = "users.bulk_delete"

    # ======================== RBAC ========================
    ROLES_VIEW = "roles.view"
    ROLES_MANAGE = "roles.manage"
    PERMISSIONS_MANAGE = "permissions.manage"

    # ======================== AUDIT & SECURITY ========================
    AUDIT_VIEW = "audit.view"
    AUDIT_EXPORT = "audit.export"
    AUDIT_CLEANUP = "audit.cleanup"

    # ======================== SESSIONS ========================
    SESSIONS_VIEW = "sessions.view"
    SESSIONS_REVOKE = "sessions.revoke"
    SESSIONS_REVOKE_ALL = "sessions.revoke_all"

    # ======================== ASSETS ========================
    ASSETS_VIEW = "assets.view"
    ASSETS_CREATE = "assets.create"
    ASSETS_UPDATE = "assets.update"
    ASSETS_DELETE = "assets.delete"
    ASSETS_ASSIGNMENTS_VIEW = "assets.assignments.view"
    ASSETS_ASSIGN = "assets.assign"
    ASSETS_UNASSIGN = "assets.unassign"
    ASSETS_TRANSFER = "assets.transfer"
    ASSETS_EXPORT = "assets.export"
    ASSETS_ARCHIVE = "assets.archive"

    # ======================== APPROVALS ========================
    APPROVALS_VIEW = "approvals.view"
    APPROVALS_CREATE = "approvals.create"
    APPROVALS_APPROVE = "approvals.approve"
    APPROVALS_REJECT = "approvals.reject"

    # ======================== REPAIRS ========================
    REPAIRS_VIEW = "repairs.view"
    REPAIRS_CREATE = "repairs.create"
    REPAIRS_UPDATE = "repairs.update"
    REPAIRS_COMPLETE = "repairs.complete"
    REPAIRS_EXPORT = "repairs.export"

    # ======================= Models =============================
    MODELS_VIEW = "models.view"
    MODELS_CREATE = "models.create"
    MODELS_UPDATE = "models.update"
    MODELS_DELETE = "models.delete"
    MODELS_EXPORT = "models.export"

    # =================== Classes ==========================
    CLASSES_VIEW = "classes.view"
    CLASSES_CREATE = "classes.create"
    CLASSES_UPDATE = "classes.update"
    CLASSES_DELETE = "classes.delete"
    CLASSES_EXPORT = "classes.export"

    # =============== Categories ==================
    CATEGORIES_VIEW = "categories.view"
    CATEGORIES_CREATE = "categories.create"
    CATEGORIES_UPDATE = "categories.update"
    CATEGORIES_DELETE = "categories.delete"
    CATEGORIES_EXPORT = "categories.export"

    # ==================== Maintenance =========================
    MAINTENANCE_VIEW = "maintenance.view"
    MAINTENANCE_CREATE = "maintenance.create"
    MAINTENANCE_UPDATE = "maintenance.update"
    MAINTENANCE_DELETE = "maintenance.delete"
    MAINTENANCE_EXPORT = "maintenance.export"

    # ==================== Images ============================
    IMAGES_VIEW = "images.view"
    IMAGES_UPLOAD = "images.upload"
    IMAGES_UPDATE = "images.UPDATE"
    IMAGES_DELETE = "images.delete"

    # ======================== DOCUMENTS ========================
    DOCUMENTS_VIEW = "documents.view"
    DOCUMENTS_CREATE = "documents.create"
    DOCUMENTS_UPDATE = "documents.update"
    DOCUMENTS_DELETE = "documents.delete"
    DOCUMENTS_EXPORT = "documents.export"

    # ======================== ANALYTICS ========================
    ANALYTICS_VIEW = "analytics.view"
    ANALYTICS_DASHBOARD = "analytics.dashboard"
    ANALYTICS_EXPORT = "analytics.export"
    ANALYTICS_FORECAST = "analytics.forecast"

    # ======================== ORGANIZATION ========================
    ORG_REGIONS_VIEW = "org.regions.view"
    ORG_REGIONS_CREATE = "org.regions.create"
    ORG_REGIONS_UPDATE = "org.regions.update"
    ORG_REGIONS_DELETE = "org.regions.delete"

    ORG_SERVICES_VIEW = "org.services.view"
    ORG_SERVICES_CREATE = "org.services.create"
    ORG_SERVICES_UPDATE = "org.services.update"
    ORG_SERVICES_DELETE = "org.services.delete"

    # ======================== WAREHOUSE ========================
    WAREHOUSE_VIEW = "warehouse.view"
    WAREHOUSE_CREATE = "warehouse.create"
    WAREHOUSE_UPDATE = "warehouse.update"
    WAREHOUSE_DELETE = "warehouse.delete"
    WAREHOUSE_EXPORT = "warehouse.export"

    # ====================== MANUFACTURE ==========================
    MANUFACTURE_VIEW = "manufacture.view"
    MANUFACTURE_CREATE = "manufacture.create"
    MANUFACTURE_UPDATE = "manufacture.update"
    MANUFACTURE_DELETE = "manufacture.delete"
    MANUFACTURE_EXPORT = "manufacture.export"

    # ======================== SYSTEM ========================
    SYSTEM_SETTINGS = "system.settings"
    SYSTEM_HEALTH = "system.health"
    SYSTEM_LOGS = "system.logs"

    # ======================== EXPENSES ========================
    EXPENSES_VIEW = "expenses.view"
    EXPENSES_CREATE = "expenses.create"
    EXPENSES_UPDATE = "expenses.update"
    EXPENSES_DELETE = "expenses.delete"
    EXPENSES_EXPORT = "expenses.export"

    @classmethod
    def all(cls) -> set[str]:
        return {
            value
            for name, value in vars(cls).items()
            if name.isupper() and isinstance(value, str) and "." in value
        }

    @classmethod
    def by_prefix(cls, prefix: str) -> set[str]:
        prefix = prefix.rstrip(".") + "."
        return {p for p in cls.all() if p.startswith(prefix)}

    @classmethod
    def validate(cls) -> None:
        seen: dict[str, str] = {}
        duplicates: list[str] = []

        for name, value in vars(cls).items():
            if not name.isupper() or not isinstance(value, str) or "." not in value:
                continue

            if value in seen and seen[value] != name:
                duplicates.append(f"{seen[value]} and {name} -> {value}")
            else:
                seen[value] = name

        if duplicates:
            raise ValueError(
                "Duplicate permission values found: " + ", ".join(duplicates)
            )


# ======================== ROLE DEFAULT SETS ========================

BASE_READ = _set(
    Permissions.USERS_VIEW,
    Permissions.SESSIONS_VIEW,
    Permissions.SYSTEM_HEALTH,
)

OPERATOR_PERMS = _set(
    *BASE_READ,
    Permissions.ASSETS_VIEW,
    Permissions.ASSETS_CREATE,
    Permissions.ASSETS_UPDATE,
    Permissions.WAREHOUSE_VIEW,
    Permissions.WAREHOUSE_CREATE,
    Permissions.WAREHOUSE_UPDATE,
    Permissions.MANUFACTURE_VIEW,
    Permissions.MANUFACTURE_CREATE,
    Permissions.MANUFACTURE_UPDATE,
    Permissions.REPAIRS_VIEW,
    Permissions.REPAIRS_CREATE,
    Permissions.REPAIRS_UPDATE,
    Permissions.MODELS_VIEW,
    Permissions.MODELS_CREATE,
    Permissions.MODELS_UPDATE,
    Permissions.CLASSES_VIEW,
    Permissions.CLASSES_CREATE,
    Permissions.CLASSES_UPDATE,
    Permissions.CATEGORIES_VIEW,
    Permissions.CATEGORIES_CREATE,
    Permissions.CATEGORIES_UPDATE,
    Permissions.IMAGES_VIEW,
    Permissions.IMAGES_UPLOAD,
    Permissions.IMAGES_UPDATE,
    Permissions.MAINTENANCE_VIEW,
    Permissions.MAINTENANCE_CREATE,
    Permissions.MAINTENANCE_UPDATE,
    Permissions.DOCUMENTS_VIEW,
    Permissions.DOCUMENTS_CREATE,
    Permissions.DOCUMENTS_UPDATE,
    Permissions.APPROVALS_VIEW,
    Permissions.APPROVALS_CREATE,
    Permissions.ANALYTICS_VIEW,
)

APPROVER_PERMS = _set(
    Permissions.APPROVALS_VIEW,
    Permissions.APPROVALS_APPROVE,
    Permissions.APPROVALS_REJECT,
    Permissions.ASSETS_VIEW,
    Permissions.ASSETS_ASSIGNMENTS_VIEW,
    Permissions.REPAIRS_VIEW,
    Permissions.MODELS_VIEW,
    Permissions.IMAGES_VIEW,
    Permissions.MAINTENANCE_VIEW,
    Permissions.DOCUMENTS_VIEW,
    Permissions.CLASSES_VIEW,
    Permissions.CATEGORIES_VIEW,
    Permissions.ANALYTICS_VIEW,
)

ANALYST_PERMS = _set(
    Permissions.AUDIT_VIEW,
    Permissions.AUDIT_EXPORT,
    Permissions.USERS_VIEW,
    Permissions.ASSETS_VIEW,
    Permissions.ASSETS_EXPORT,
    Permissions.ASSETS_ASSIGNMENTS_VIEW,
    Permissions.REPAIRS_VIEW,
    Permissions.REPAIRS_EXPORT,
    Permissions.MODELS_VIEW,
    Permissions.MODELS_EXPORT,
    Permissions.IMAGES_VIEW,
    Permissions.MAINTENANCE_VIEW,
    Permissions.MAINTENANCE_EXPORT,
    Permissions.DOCUMENTS_VIEW,
    Permissions.DOCUMENTS_EXPORT,
    Permissions.CLASSES_VIEW,
    Permissions.CLASSES_EXPORT,
    Permissions.CATEGORIES_VIEW,
    Permissions.CATEGORIES_EXPORT,
    Permissions.WAREHOUSE_VIEW,
    Permissions.WAREHOUSE_EXPORT,
    Permissions.MANUFACTURE_VIEW,
    Permissions.MANUFACTURE_EXPORT,
    Permissions.ANALYTICS_VIEW,
    Permissions.ANALYTICS_DASHBOARD,
    Permissions.ANALYTICS_EXPORT,
    Permissions.ANALYTICS_FORECAST,
    Permissions.EXPENSES_VIEW,
    Permissions.EXPENSES_EXPORT,
    Permissions.SYSTEM_HEALTH,
    Permissions.SYSTEM_LOGS,
)

ADMIN_PERMS = _set(
    Permissions.USERS_VIEW,
    Permissions.USERS_CREATE,
    Permissions.USERS_EDIT,
    Permissions.USERS_DELETE,
    Permissions.USERS_PASSWORD_RESET,
    Permissions.USERS_BULK_EDIT,
    Permissions.USERS_BULK_DELETE,
    Permissions.SESSIONS_VIEW,
    Permissions.SESSIONS_REVOKE,
    Permissions.SESSIONS_REVOKE_ALL,
    Permissions.ROLES_VIEW,
    Permissions.ASSETS_VIEW,
    Permissions.ASSETS_CREATE,
    Permissions.ASSETS_UPDATE,
    Permissions.ASSETS_DELETE,
    Permissions.ASSETS_ASSIGN,
    Permissions.ASSETS_ASSIGNMENTS_VIEW,
    Permissions.ASSETS_UNASSIGN,
    Permissions.ASSETS_TRANSFER,
    Permissions.ASSETS_EXPORT,
    Permissions.ASSETS_ARCHIVE,
    Permissions.REPAIRS_VIEW,
    Permissions.REPAIRS_CREATE,
    Permissions.REPAIRS_UPDATE,
    Permissions.REPAIRS_COMPLETE,
    Permissions.REPAIRS_EXPORT,
    Permissions.MODELS_VIEW,
    Permissions.MODELS_CREATE,
    Permissions.MODELS_UPDATE,
    Permissions.MODELS_DELETE,
    Permissions.MODELS_EXPORT,
    Permissions.CLASSES_VIEW,
    Permissions.CLASSES_CREATE,
    Permissions.CLASSES_UPDATE,
    Permissions.CLASSES_DELETE,
    Permissions.CLASSES_EXPORT,
    Permissions.CATEGORIES_VIEW,
    Permissions.CATEGORIES_CREATE,
    Permissions.CATEGORIES_UPDATE,
    Permissions.CATEGORIES_DELETE,
    Permissions.CATEGORIES_EXPORT,
    Permissions.IMAGES_VIEW,
    Permissions.IMAGES_UPLOAD,
    Permissions.IMAGES_UPDATE,
    Permissions.IMAGES_DELETE,
    Permissions.MAINTENANCE_VIEW,
    Permissions.MAINTENANCE_CREATE,
    Permissions.MAINTENANCE_UPDATE,
    Permissions.MAINTENANCE_DELETE,
    Permissions.MAINTENANCE_EXPORT,
    Permissions.DOCUMENTS_VIEW,
    Permissions.DOCUMENTS_CREATE,
    Permissions.DOCUMENTS_UPDATE,
    Permissions.DOCUMENTS_DELETE,
    Permissions.DOCUMENTS_EXPORT,
    Permissions.APPROVALS_VIEW,
    Permissions.APPROVALS_CREATE,
    Permissions.APPROVALS_APPROVE,
    Permissions.APPROVALS_REJECT,
    Permissions.WAREHOUSE_VIEW,
    Permissions.WAREHOUSE_CREATE,
    Permissions.WAREHOUSE_UPDATE,
    Permissions.WAREHOUSE_DELETE,
    Permissions.WAREHOUSE_EXPORT,
    Permissions.MANUFACTURE_VIEW,
    Permissions.MANUFACTURE_CREATE,
    Permissions.MANUFACTURE_UPDATE,
    Permissions.MANUFACTURE_DELETE,
    Permissions.MANUFACTURE_EXPORT,
    Permissions.ORG_REGIONS_VIEW,
    Permissions.ORG_REGIONS_CREATE,
    Permissions.ORG_REGIONS_UPDATE,
    Permissions.ORG_REGIONS_DELETE,
    Permissions.ORG_SERVICES_VIEW,
    Permissions.ORG_SERVICES_CREATE,
    Permissions.ORG_SERVICES_UPDATE,
    Permissions.ORG_SERVICES_DELETE,
    Permissions.EXPENSES_VIEW,
    Permissions.EXPENSES_CREATE,
    Permissions.EXPENSES_UPDATE,
    Permissions.EXPENSES_DELETE,
    Permissions.EXPENSES_EXPORT,
    Permissions.AUDIT_VIEW,
    Permissions.ANALYTICS_VIEW,
    Permissions.SYSTEM_SETTINGS,
    Permissions.SYSTEM_HEALTH,
)

# ======================== ROLE -> PERMISSIONS ========================
# Keep keys as role values so the map is stable across StrEnum usage.
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    UserRole.SUPERADMIN.value: frozenset(Permissions.all()),
    UserRole.ADMIN.value: ADMIN_PERMS,
    UserRole.OPERATOR.value: OPERATOR_PERMS,
    UserRole.APPROVER.value: APPROVER_PERMS,
    UserRole.ANALYST.value: ANALYST_PERMS,
}


def normalize_role(role: UserRole | str) -> str:
    return role.value if isinstance(role, UserRole) else role


def get_permissions_for_role(role: UserRole | str) -> frozenset[str]:
    return ROLE_PERMISSIONS.get(normalize_role(role), frozenset())


def has_permission(role: UserRole | str, permission: str) -> bool:
    return permission in get_permissions_for_role(role)


def is_valid_permission(permission: str) -> bool:
    return permission in Permissions.all()
