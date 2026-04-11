from collections.abc import Callable

from fastapi import Depends
from core.exceptions.errors import PermissionDenied
from core.security.dependencies import get_current_user
from core.security.types import CurrentUser


def require_permissions(required: list[str]) -> Callable[..., bool]:
    def checker(user: CurrentUser = Depends(get_current_user)) -> bool:
        user_permissions = user.get("permissions", [])

        missing = [perm for perm in required if perm not in user_permissions]

        if missing:
            raise PermissionDenied(
                detail=f"Missing permissions: {','.join(missing)}",
                values={"missing": missing}
            )
        return True
    return checker


def require_any_permission(required: list[str]) -> Callable[..., bool]:
    def checker(user: CurrentUser = Depends(get_current_user)) -> bool:
        user_permissions = user.get("permissions", [])

        if not any(perm in user_permissions for perm in required):
            raise PermissionDenied(
                detail="You don't have any required permission",
                values={"required": required}
            )
        return True
    return checker


def require_any_role(required: list[str]) -> Callable[..., bool]:
    def checker(user: CurrentUser = Depends(get_current_user)) -> bool:
        user_role = user.get("role")

        if user_role not in required:
            raise PermissionDenied(
                detail=f"Forbidden required roles: {', '.join(required)}",
                values={"required": required}
            )
        return True
    return checker


def require_self_or_permission(permission: str) -> Callable[..., bool]:
    def checker(
        user: CurrentUser = Depends(get_current_user),
        target_user_id: str | None = None,
    ) -> bool:
        if user["sub"] == target_user_id:
            return True

        if permission not in user.get("permissions", []):
            raise PermissionDenied()

        return True

    return checker
