from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from pydantic import ValidationError

from core.config import get_settings
from core.exceptions.errors import InvalidToken, TokenExpired
from schemas.auth import TokenPayloadSchema

settings = get_settings()


def _base_payload(user_id: str, token_type: str) -> dict[str, object]:
    now = datetime.now(UTC)

    return {
        "sub": str(user_id),
        "type": token_type,
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }


def create_access_token(user_id: str, session_id: str) -> str:
    now = datetime.now(UTC)

    payload = _base_payload(user_id, "access")
    payload["exp"] = int(
        (now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)).timestamp()
    )
    payload["session_id"] = session_id

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str):
    now = datetime.now(UTC)

    payload = _base_payload(user_id, "refresh")
    payload["exp"] = int(
        (now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()
    )

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, str(payload["jti"])


async def decode_token(
    token: str, expected_type: str | None = None
) -> TokenPayloadSchema:
    try:
        raw = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={
                "require": ["exp", "iat", "jti", "sub", "type"],
            },
        )

        if not expected_type:
            raise InvalidToken("Token type must be enforced")

        if raw.get("type") != expected_type:
            raise InvalidToken("Invalid token type")

        return TokenPayloadSchema(
            sub=UUID(raw["sub"]),
            jti=UUID(raw["jti"]),
            exp=int(raw["exp"]),
            iat=int(raw.get("iat", raw["exp"])),
            type=str(raw["type"]),
            iss=raw.get("iss"),
            aud=raw.get("aud"),
            session_id=UUID(raw["session_id"]) if raw.get("session_id") else None,
        )

    except jwt.ExpiredSignatureError as e:
        raise TokenExpired() from e

    except (jwt.PyJWTError, ValidationError, KeyError, TypeError, ValueError) as e:
        raise InvalidToken("Invalid token") from e
