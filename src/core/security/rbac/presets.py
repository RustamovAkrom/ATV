from db.models.enums import UserRole
from core.security.permissions import Permissions
from core.security.rbac.guards import require_roles, require_permissions


# =========================
# ROLE PRESETS
# =========================
IsSuperAdmin = require_roles(UserRole.SUPERADMIN)

IsAdmin = require_roles(
    UserRole.ADMIN,
    UserRole.SUPERADMIN,
)

IsModerator = require_roles(
    UserRole.MODERATOR,
    UserRole.SUPERADMIN,
)

IsAnalytic = require_roles(
    UserRole.ANALYTIC,
    UserRole.SUPERADMIN,
)


# =========================
# PERMISSION PRESETS
# =========================
CanReadUsers = require_permissions(Permissions.USERS_READ)
CanCreateUsers = require_permissions(Permissions.USERS_CREATE)
CanUpdateUsers = require_permissions(Permissions.USERS_UPDATE)
CanDeleteUsers = require_permissions(Permissions.USERS_DELETE)

CanReadAudit = require_permissions(Permissions.AUDIT_READ)

CanReadSessions = require_permissions(Permissions.SESSIONS_READ)
CanDeleteSessions = require_permissions(Permissions.SESSIONS_DELETE)
