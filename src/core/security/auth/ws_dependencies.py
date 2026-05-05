from fastapi import WebSocket, Depends

from core.security.jwt import decode_token
from core.security.blacklist import get_blacklist
from core.exceptions.errors import InvalidToken
from api.dependencies.users import get_user_repo
from repositories.users.user_repo import UserRepository
from schemas.auth import CurrentUserSchema


async def get_current_user_ws(
    websocket: WebSocket,
    user_repo: UserRepository = Depends(get_user_repo),
) -> CurrentUserSchema:

    token = websocket.query_params.get("token")

    if not token:
        raise InvalidToken("Missing token")

    payload = await decode_token(token, expected_type="access")

    if await get_blacklist().contains(payload.jti):
        raise InvalidToken()

    if not payload.session_id:
        raise InvalidToken("Session required")

    user = await user_repo.get_by_id(payload.sub)
    if not user:
        raise InvalidToken()

    return CurrentUserSchema(
        id=user.id,
        role=user.role.code.lower() if user.role else None,
        permissions=[str(p).lower() for p in (user.permissions or [])],
        assigned_region_id=user.assigned_region_id,
        assigned_service_id=user.assigned_service_id,
    )
