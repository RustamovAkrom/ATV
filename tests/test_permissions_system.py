import pytest

from core.exceptions.errors import PermissionDenied
from core.security.permissions import (
    require_any_permission,
    require_permissions,
    require_role_and_permissions,
    require_roles,
)
from db.models.enums import UserRole


def _build_user(
    *,
    role: str | None = None,
    permissions: list[str] | None = None,
    sub: str = "00000000-0000-0000-0000-000000000001",
) -> dict:
    return {
        "sub": sub,
        "jti": None,
        "type": "access",
        "exp": 0,
        "role": role,
        "permissions": permissions or [],
    }


async def _run_dependency(dependency, user: dict) -> dict:
    return await dependency(user=user)


@pytest.mark.anyio
async def test_require_roles_accepts_role_code_and_enum() -> None:
    dependency = require_roles("superadmin", UserRole.ADMIN)
    user = _build_user(role="admin")

    result = await _run_dependency(dependency, user)

    assert result is user


@pytest.mark.anyio
async def test_require_roles_rejects_when_role_is_name_not_code() -> None:
    dependency = require_roles(UserRole.SUPERADMIN)
    user = _build_user(role="SUPERADMIN")

    with pytest.raises(PermissionDenied) as exc_info:
        await _run_dependency(dependency, user)

    assert exc_info.value.values == {
        "current": "SUPERADMIN",
        "required": ["superadmin"],
    }


@pytest.mark.anyio
async def test_require_permissions_reports_missing_permissions_sorted() -> None:
    dependency = require_permissions("audit.read", "assets.read")
    user = _build_user(permissions=["assets.read"])

    with pytest.raises(PermissionDenied) as exc_info:
        await _run_dependency(dependency, user)

    assert exc_info.value.values == {
        "missing": ["audit.read"],
        "required": ["assets.read", "audit.read"],
    }


@pytest.mark.anyio
async def test_require_any_permission_accepts_one_match() -> None:
    dependency = require_any_permission("users.delete", "audit.read")
    user = _build_user(permissions=["audit.read"])

    result = await _run_dependency(dependency, user)

    assert result is user


@pytest.mark.anyio
async def test_require_role_and_permissions_validates_both_dimensions() -> None:
    dependency = require_role_and_permissions(
        roles=[UserRole.ADMIN, UserRole.SUPERADMIN],
        permissions=["assets.read", "audit.read"],
    )
    user = _build_user(role="admin", permissions=["assets.read"])

    with pytest.raises(PermissionDenied) as exc_info:
        await _run_dependency(dependency, user)

    assert exc_info.value.values == {
        "missing": ["audit.read"],
        "required_permissions": ["assets.read", "audit.read"],
    }
