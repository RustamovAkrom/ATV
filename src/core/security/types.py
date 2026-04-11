from typing import TypedDict


class CurrentUser(TypedDict):
    sub: str
    jti: str | None
    type: str
    role: str | None
    permissions: list[str]
