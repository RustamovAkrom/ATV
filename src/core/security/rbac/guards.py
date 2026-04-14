from fastapi import Depends
from core.exceptions.errors import PermissionDenied
from core.security.auth.dependencies import get_current_user
from core.security.auth.types import CurrentUser


def require_roles(*roles: str):
    async def checker(user: CurrentUser = Depends(get_current_user)):
        if not user.has_role(*roles):
            raise PermissionDenied(
                detail="Invalid role",
                values={"required": roles},
            )
        return user

    return checker


def require_permissions(*permissions: str):
    async def checker(user: CurrentUser = Depends(get_current_user)):
        if not user.has_permission(*permissions):
            raise PermissionDenied(
                detail="Missing permissions",
                values={"missing": permissions},
            )
        return user

    return checker
