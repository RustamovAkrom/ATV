from typing import TypedDict
from uuid import UUID

class CurrentUser(TypedDict):
    sub: UUID
    jti: UUID | None
    type: str
    role: str | None
    permissions: list[str]
