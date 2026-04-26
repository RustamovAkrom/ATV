from db.models.enums import UserRole


class Permissions:
    # --- USERS & PROFILE ---
    USERS_VIEW = "users.view"
    USERS_CREATE = "users.create"
    USERS_EDIT = "users.edit"
    USERS_DELETE = "users.delete"
    USERS_PASSWORD_RESET = "users.password_reset"  # Сброс чужих паролей

    # --- RBAC (Roles & Permissions) ---
    ROLES_VIEW = "roles.view"
    ROLES_MANAGE = "roles.manage"

    # --- AUDIT & SECURITY LOGS ---
    AUDIT_VIEW = "audit.view"
    AUDIT_EXPORT = "audit.export"
    AUDIT_CLEANUP = "audit.cleanup"  # Только для SuperAdmin

    # --- SESSIONS ---
    SESSIONS_VIEW = "sessions.view"
    SESSIONS_REVOKE = "sessions.revoke"

    # --- ASSETS & FILES ---
    ASSETS_VIEW = "assets.view"
    ASSETS_CREATE = "assets.create"
    ASSETS_UPDATE = "assets.update"
    ASSETS_DELETE = "assets.delete"
    ASSETS_EXPORT = "assets.export"

    # --- SYSTEM ---
    SYSTEM_SETTINGS = "system.settings"
    SYSTEM_HEALTH = "system.health"

    @classmethod
    def all(cls) -> set[str]:
        return {
            v
            for k, v in cls.__dict__.items()
            if isinstance(v, str) and not k.startswith("_") and "." in v
        }


# Вспомогательные наборы прав для упрощения маппинга
MODERATOR_BASE = {
    Permissions.USERS_VIEW,
    Permissions.SESSIONS_VIEW,
    Permissions.ASSETS_VIEW,
}

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
}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    # Божественный доступ
    UserRole.SUPERADMIN.value: Permissions.all(),
    # Полное управление операционкой, но без удаления системы и очистки аудита
    UserRole.ADMIN.value: ADMIN_BASE
    | {
        Permissions.AUDIT_VIEW,
        Permissions.SYSTEM_HEALTH,
    },
    # Просмотр и базовая модерация
    UserRole.MODERATOR.value: MODERATOR_BASE,
    # Офицер безопасности / Аналитик
    UserRole.ANALYTIC.value: {
        Permissions.AUDIT_VIEW,
        Permissions.AUDIT_EXPORT,
        Permissions.USERS_VIEW,
        Permissions.ASSETS_VIEW,
        Permissions.ASSETS_EXPORT,
        Permissions.SYSTEM_HEALTH,
    },
}
