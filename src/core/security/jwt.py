from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4, UUID

import jwt

from core.config import get_settings
from core.exceptions.errors import TokenExpired, InvalidToken


settings = get_settings()

def _base_payload(user_id: str, token_type: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc)

    return {
        "sub": user_id,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE
    }


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)

    payload = _base_payload(user_id, "access")
    payload["exp"] = int(
        (now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)).timestamp()
    )

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> tuple[str, str]:
    now = datetime.now(timezone.utc)

    payload = _base_payload(user_id, "refresh")
    payload["exp"] = int(
        (now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()
    )

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, payload['jti']


async def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    try:
        raw = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )

        payload = {
            "sub": UUID(raw["sub"]),
            "jti": UUID(raw["jti"]),
            "type": raw["type"],
            "exp": raw.get("exp"),
            "iat": raw.get("iat"),
        }

        if expected_type and payload["type"] != expected_type:
            raise InvalidToken("Invalid token type")

        return payload

    except jwt.ExpiredSignatureError:
        raise TokenExpired()

    except jwt.PyJWTError:
        raise InvalidToken()
