from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List


def _normalize_role(value: object) -> str:
    return str(getattr(value, "value", value)).lower()


def _normalize_permission(value: object) -> str:
    return str(getattr(value, "value", value))


class CurrentUser(BaseModel):
    id: UUID
    role: Optional[str]
    permissions: List[str] = Field(default_factory=list)

    def has_role(self, *roles: str) -> bool:
        normalized = {_normalize_role(role) for role in roles}
        return self.role in normalized

    def has_permission(self, *perms: str) -> bool:
        normalized = {_normalize_permission(perm) for perm in perms}
        return normalized.issubset(set(self.permissions))


class TokenPayload(BaseModel):
    sub: UUID
    jti: UUID
    exp: int
    iat: int
    type: str
    iss: Optional[str] = None
    aud: Optional[str] = None
    session_id: Optional[UUID] = None
