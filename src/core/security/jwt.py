from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID
import jwt

from core.config import get_settings
from core.exceptions.errors import InvalidToken, TokenExpired
from core.security.auth.types import TokenPayload

settings = get_settings()


def _base_payload(user_id: str, token_type: str):
    now = datetime.now(timezone.utc)

    return {
        "sub": str(user_id),
        "type": token_type,
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)

    payload = _base_payload(user_id, "access")
    payload["exp"] = int(
        (now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)).timestamp()
    )

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str):
    now = datetime.now(timezone.utc)

    payload = _base_payload(user_id, "refresh")
    payload["exp"] = int(
        (now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()
    )

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, payload["jti"]


async def decode_token(token: str, expected_type: str | None = None) -> TokenPayload:
    try:
        raw = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )

        if expected_type and raw.get("type") != expected_type:
            raise InvalidToken()

        return TokenPayload(
            sub=UUID(raw["sub"]),
            jti=UUID(raw["jti"]),
            exp=raw["exp"],
            type=raw["type"],
        )

    except jwt.ExpiredSignatureError:
        raise TokenExpired()

    except jwt.PyJWTError:
        raise InvalidToken()
