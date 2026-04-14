from typing import Dict, Set
from db.models.enums import UserRole


# PERMISSIONS
class Permissions:
    # USERS
    USERS_READ = "users.read"
    USERS_CREATE = "users.create"
    USERS_UPDATE = "users.update"
    USERS_DELETE = "users.delete"

    # RBAC
    ROLES_READ = "roles.read"
    ROLES_UPDATE = "roles.update"

    # SESSIONS
    SESSIONS_READ = "sessions.read"
    SESSIONS_DELETE = "sessions.delete"

    # AUDIT
    AUDIT_READ = "audit.read"

    # ASSETS
    ASSETS_READ = "assets.read"
    ASSETS_WRITE = "assets.write"

    @classmethod
    def all(cls) -> Set[str]:
        return {
            v
            for k, v in cls.__dict__.items()
            if not k.startswith("_") and isinstance(v, str)
        }


# ROLE → PERMISSIONS
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    UserRole.SUPERADMIN.value: Permissions.all(),

    UserRole.ADMIN.value: {
        Permissions.USERS_READ,
        Permissions.USERS_CREATE,
        Permissions.USERS_UPDATE,
        Permissions.SESSIONS_READ,
        Permissions.ASSETS_READ,
        Permissions.ASSETS_WRITE,
    },

    UserRole.MODERATOR.value: {
        Permissions.USERS_READ,
        Permissions.SESSIONS_READ,
        Permissions.ASSETS_READ,
    },

    UserRole.ANALYTIC.value: {
        Permissions.AUDIT_READ,
        Permissions.ASSETS_READ,
    },
}
