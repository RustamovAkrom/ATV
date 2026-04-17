from fastapi import Depends, Request

from core.exceptions.errors import InvalidToken
from core.security.blacklist import get_blacklist
from core.security.jwt import decode_token
from core.security.auth.types import CurrentUser
from repositories.user_repo import UserRepository
from api.dependencies.users import get_user_repo
from .extractor import extract_token


async def get_token_payload(
    request: Request,
    token: str = Depends(extract_token),
):
    payload = await decode_token(token, expected_type="access")

    if await get_blacklist().contains(payload.jti):
        raise InvalidToken()

    request.state.user_id = str(payload.sub)
    request.state.access_payload = payload
    request.state.session_id = payload.session_id

    return payload


# CURRENT USER (DB слой)
async def get_current_user(
    payload = Depends(get_token_payload),
    user_repo: UserRepository = Depends(get_user_repo),
) -> CurrentUser:

    user = await user_repo.get_by_id(payload.sub)
    if not user:
        raise InvalidToken()

    if user.last_password_change and payload.iat:
        if payload.iat <= int(user.last_password_change.timestamp()):
            raise InvalidToken("Token outdated")

    role_code = getattr(user.role, "code", None)
    permissions = [
        str(getattr(permission, "code", getattr(permission, "value", permission)))
        for permission in (user.permissions or [])
    ]

    return CurrentUser(
        id=user.id,
        role=user.role.code.lower() if user.role else None,
        permissions=permissions,
    )
