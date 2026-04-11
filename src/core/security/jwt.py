from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt

from core.config import get_settings


settings = get_settings()


def _base_payload(user_id: str, token_type: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc)

    return {
        "sub": user_id,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": now,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE
    }


def create_access_token(user_id: str) -> str:
    payload = _base_payload(user_id, "access")

    payload.update({
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)
    })
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> tuple[str, str]:
    payload = _base_payload(user_id, token_type="refresh")

    payload.update({
        "exp": datetime.now(timezone.utc)
        + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    })

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, payload['jti']


async def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )

        # if await is_blacklisted(payload['jti']):
        #     raise InvalidToken(detail="Token revoked")

        return payload

    except jwt.ExpiredSignatureError:
        from core.exceptions.errors import TokenExpired
        raise TokenExpired()

    except jwt.PyJWTError:
        from core.exceptions.errors import InvalidToken
        raise InvalidToken()
