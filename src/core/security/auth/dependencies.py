from fastapi import Depends, Request

from core.exceptions.errors import InvalidToken
from core.security.blacklist import get_blacklist
from core.security.jwt import decode_token
from core.security.auth.types import CurrentUser
from repositories.user_repo import UserRepository
from api.dependencies.users import get_user_repo
from .extractor import extract_token


# PAYLOAD (JWT слой)
async def get_token_payload(
    request: Request,
    token: str = Depends(extract_token),
):
    payload = await decode_token(token, expected_type="access")

    # write for audit
    request.state.user_id = str(payload.sub)
    request.state.access_payload = payload
    request.state.session_id = getattr(payload, "session_id", None)

    # blacklist check
    if await get_blacklist().contains(payload.jti):
        raise InvalidToken()

    return payload


# CURRENT USER (DB слой)
async def get_current_user(
    payload = Depends(get_token_payload),
    user_repo: UserRepository = Depends(get_user_repo),
) -> CurrentUser:

    user = await user_repo.get_by_id(payload.sub)
    if not user:
        raise InvalidToken()

    return CurrentUser(
        id=user.id,
        role=user.role.code.lower() if user.role else None,
        permissions=user.permissions or [],
    )
