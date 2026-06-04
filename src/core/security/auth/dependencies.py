from uuid import UUID

from fastapi import Depends, Request

from api.dependencies.users import get_user_repo
from core.exceptions.errors import InvalidToken
from core.security.blacklist import get_blacklist
from core.security.jwt import decode_token
from core.security.rbac.permissions import Permissions
from db.models.enums import UserRole, UserStatus
from db.models.users.user import User
from repositories.users.user_repo import UserRepository
from schemas.auth import CurrentUserSchema

from .extractor import extract_token

VALID_PERMISSIONS = set(Permissions.all())
VALID_ROLES = {r.value for r in UserRole}


async def get_token_payload(
    request: Request,
    token: str = Depends(extract_token),
):
    payload = await decode_token(token, expected_type="access")

    if await get_blacklist().contains(str(payload.jti)):
        raise InvalidToken()

    if not payload.session_id:
        raise InvalidToken("Session required")

    request.state.user_id = str(payload.sub)
    request.state.access_payload = payload
    request.state.session_id = payload.session_id

    return payload


async def get_current_user(
    payload=Depends(get_token_payload),
    user_repo: UserRepository = Depends(get_user_repo),
) -> CurrentUserSchema:

    user: User | None = await user_repo.get_by_id(payload.sub)
    if not user:
        raise InvalidToken()

    if user.status != UserStatus.ACTIVE:
        raise InvalidToken("User inactive")

    if (
        user.last_password_change
        and payload.iat
        and payload.iat <= int(user.last_password_change.timestamp())
    ):
        raise InvalidToken("Token outdated")

    permissions = list(
        VALID_PERMISSIONS.intersection(
            {str(p).lower() for p in (user.permissions or [])}
        )
    )

    role = (
        user.role.slug.lower() if user.role and user.role.slug in VALID_ROLES else None
    )

    return CurrentUserSchema(
        id=UUID(str(user.id)),
        role=role,
        permissions=permissions,
        assigned_department_id=user.department_id,
        assigned_region_id=user.assigned_region_id,
        assigned_service_id=user.assigned_service_id,
    )
