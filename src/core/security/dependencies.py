from uuid import UUID

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import SQLAlchemyError

from repositories.user_repo import UserRepository, get_user_repo
from core.security.jwt import decode_token
from core.exceptions.errors import InvalidToken, AuthenticationError
from core.security.types import CurrentUser


security = HTTPBearer(auto_error=False)


def extract_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    # 1. Header (priority)
    if credentials:
        return credentials.credentials

    # w. Cookie fallback
    token = request.cookies.get("access_token")
    if token:
        return token
    raise AuthenticationError(detail="Not authenticated")


async def get_current_user(
    token: str = Depends(extract_token),
    user_repo: UserRepository = Depends(get_user_repo),
) -> CurrentUser:
    try:
        payload = await decode_token(token)

        if payload.get("type") != "access":
            raise InvalidToken()

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidToken()

        user = await user_repo.get_by_id(UUID(user_id))
        if not user:
            raise InvalidToken()

        return {
            "sub": str(user.id),
            "jti": payload.get("jti"),
            "type": payload.get("type"),
            "role": user.role.name if user.role else None,
            "permissions": user.permissions,
        }

    except (InvalidToken, AuthenticationError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    except SQLAlchemyError:
        raise
