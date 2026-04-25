from fastapi import Depends

from core.security.rbac.guards import require_permission, require_role
from core.security.rbac.permissions import Permissions
from db.models.enums import UserRole

# =================================================================
# ROLE-BASED PRESETS (Жесткие проверки по роли)
# =================================================================

# Только для разработчика/главного админа
IsSuperAdmin = Depends(require_role(UserRole.SUPERADMIN.value))

# Для административного персонала (пропустит и супера)
IsAdmin = Depends(require_role(UserRole.ADMIN.value))

# Для модераторов
IsModerator = Depends(require_role(UserRole.MODERATOR.value))

# Любой сотрудник (не обычный юзер)
IsStaff = Depends(
    require_role(
        UserRole.ADMIN.value, UserRole.MODERATOR.value, UserRole.ANALYTIC.value
    )
)

IsAdminOrAnalytic = Depends(
    require_role(
        UserRole.ADMIN.value,
        UserRole.ANALYTIC.value,
    )
)


# =================================================================
# PERMISSION-BASED PRESETS (Гибкие проверки по правам)
# =================================================================

# --- Users Management ---
CanViewUsers = Depends(require_permission(Permissions.USERS_VIEW))
CanCreateUsers = Depends(require_permission(Permissions.USERS_CREATE))
CanManageUsers = Depends(
    require_permission(Permissions.USERS_EDIT, Permissions.USERS_CREATE)
)
CanDeleteUsers = Depends(require_permission(Permissions.USERS_DELETE))

# --- Audit & Security ---
CanViewAudit = Depends(require_permission(Permissions.AUDIT_VIEW))
CanExportAudit = Depends(require_permission(Permissions.AUDIT_EXPORT))
CanFullAuditControl = Depends(
    require_permission(Permissions.AUDIT_VIEW, Permissions.AUDIT_CLEANUP)
)

# --- RBAC ---
CanManageRoles = Depends(require_permission(Permissions.ROLES_MANAGE))

# --- Sessions ---
CanViewSessions = Depends(require_permission(Permissions.SESSIONS_VIEW))
CanRevokeSessions = Depends(require_permission(Permissions.SESSIONS_REVOKE))

# --- Assets ---
CanViewAssets = Depends(require_permission(Permissions.ASSETS_VIEW))
CanCreateAssets = Depends(require_permission(Permissions.ASSETS_CREATE))
CanUpdateAssets = Depends(require_permission(Permissions.ASSETS_UPDATE))
CanDeleteAssets = Depends(require_permission(Permissions.ASSETS_DELETE))
CanExportAssets = Depends(require_permission(Permissions.ASSETS_EXPORT))

# --- System ---
CanViewSystemHealth = Depends(require_permission(Permissions.SYSTEM_HEALTH))
