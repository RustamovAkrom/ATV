from uuid import UUID

from pydantic import BaseModel, Field

from db.models.enums import UserRole


class CurrentUserSchema(BaseModel):
    id: UUID
    role: str | None
    permissions: list[str] = Field(default_factory=list)

    @property
    def permission_set(self) -> set[str]:
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


class TokenPayloadSchema(BaseModel):
    sub: UUID
    jti: UUID
    exp: int
    iat: int
    type: str
    iss: str | None = None
    aud: str | None = None
    session_id: UUID | None = None


class TokenPairSchema(BaseModel):
    access_token: str
    refresh_token: str


class LoginRequestSchema(BaseModel):
    login: str
    password: str


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshRequestSchema(BaseModel):
    refresh_token: str
