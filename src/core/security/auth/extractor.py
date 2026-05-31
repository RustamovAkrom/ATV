# security/auth/extractor.py

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from core.exceptions.errors import AuthenticationError

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


def extract_token(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
) -> str:
    if token:
        return token

    cookie = request.cookies.get("access_token")
    if cookie:
        return cookie

    raise AuthenticationError("Not authenticated")
