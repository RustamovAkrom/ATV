from fastapi import Depends
from core.exceptions.errors import PermissionDenied
from core.security.auth.dependencies import get_current_user
from core.security.auth.types import CurrentUser


def require_role(*roles: str):
    async def checker(user: CurrentUser = Depends(get_current_user)):
        if not user.has_role(*roles):
            raise PermissionDenied(detail=f"Access denied. Required roles: {roles}")
        return user
    return checker

def require_permission(*permissions: str, any_of: bool = False):
    async def checker(user: CurrentUser = Depends(get_current_user)):
        if not user.has_permission(*permissions, any_of=any_of):
            raise PermissionDenied(detail="Missing required permissions")
        return user
    return checker
