from fastapi import Depends

from core.exceptions.errors import PermissionDenied
from core.security.auth.dependencies import get_current_user
from schemas.auth import CurrentUserSchema


def check_role(user: CurrentUserSchema, *roles: str):
    if not user.has_role(*roles):
        raise PermissionDenied(detail=f"Access denied. Required roles: {roles}")


def check_permissions(
    user: CurrentUserSchema, *permissions: str, any_of: bool = False
):
    if not user.has_permission(*permissions, any_of=any_of):
        raise PermissionDenied(detail="Missing required permissions")


def require_role(*roles: str):
    async def checker(user: CurrentUserSchema = Depends(get_current_user)):
        check_role(user, *roles)
        return user

    return checker


def require_permission(*permissions: str, any_of: bool = False):
    async def checker(user: CurrentUserSchema = Depends(get_current_user)):
        check_permissions(user, *permissions, any_of=any_of)
        return user

    return checker
