from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List


class CurrentUser(BaseModel):
    id: UUID
    role: Optional[str]
    permissions: List[str] = []

    def has_role(self, *roles: str) -> bool:
        return self.role in roles

    def has_permission(self, *perms: str) -> bool:
        return all(p in self.permissions for p in perms)


class TokenPayload(BaseModel):
    sub: UUID
    jti: UUID
    exp: int
    type: str
