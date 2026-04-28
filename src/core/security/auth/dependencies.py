from fastapi import Depends, Request

from api.dependencies.users import get_user_repo
from core.exceptions.errors import InvalidToken
from core.security.blacklist import get_blacklist
from core.security.jwt import decode_token
from repositories.users.user_repo import UserRepository
from schemas.auth import CurrentUserSchema
from core.security.rbac.permissions import Permissions
from db.models.enums import UserRole

from .extractor import extract_token


async def get_token_payload(
    request: Request,
    token: str = Depends(extract_token),
):
    payload = await decode_token(token, expected_type="access")

    if await get_blacklist().contains(payload.jti):
        raise InvalidToken()

    if not payload.session_id:
        raise InvalidToken("Session required")

    request.state.user_id = str(payload.sub)
    request.state.access_payload = payload
    request.state.session_id = payload.session_id

    return payload


# CURRENT USER DEPENDENCY
async def get_current_user(
    payload=Depends(get_token_payload),
    user_repo: UserRepository = Depends(get_user_repo),
) -> CurrentUserSchema:

    user = await user_repo.get_by_id(payload.sub)
    if not user:
        raise InvalidToken()

    if user.last_password_change and payload.iat:
        if payload.iat <= int(user.last_password_change.timestamp()):
            raise InvalidToken("Token outdated")

    valid_permissions = Permissions.all()

    permissions = [
        str(p).lower()
        for p in (user.permissions or [])
        if str(p).lower() in valid_permissions
    ]

    role = (
        user.role.code.lower()
        if user.role and user.role.code in {r.value for r in UserRole}
        else None
    )

    return CurrentUserSchema(
        id=user.id,
        role=role,
        permissions=permissions,
        assigned_region_id=user.assigned_region_id,
        assigned_service_id=user.assigned_service_id,
    )
