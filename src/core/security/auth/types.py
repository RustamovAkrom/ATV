from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List, Set

from db.models.enums import UserRole


class CurrentUser(BaseModel):
    id: UUID
    role: Optional[str]
    permissions: List[str] = Field(default_factory=list)

    @property
    def permission_set(self) -> Set[str]:
        if not hasattr(self, "_perm_set"):
            self._perm_set = set(self.permissions)
        return self._perm_set

    def has_role(self, *roles: str) -> bool:
        if self.role == UserRole.SUPERADMIN.value:
            return True

        normalized_required = {str(r).lower() for r in roles}
        return self.role in normalized_required

    def has_permission(self, *perms: str, any_of: bool = False) -> bool:
        if self.role == UserRole.SUPERADMIN.value:
            return True

        required = {str(p).lower() for p in perms}
        user_perms = self.permission_set

        if any_of:
            return not user_perms.isdisjoint(required)
        return required.issubset(user_perms)


class TokenPayload(BaseModel):
    sub: UUID
    jti: UUID
    exp: int
    iat: int
    type: str
    iss: Optional[str] = None
    aud: Optional[str] = None
    session_id: Optional[UUID] = None
