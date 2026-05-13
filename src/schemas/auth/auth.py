from uuid import UUID

from pydantic import Field

from db.models.enums import UserRole
from schemas.base import BaseSchema


class CurrentUserSchema(BaseSchema):
    id: UUID
    role: str | None
    permissions: list[str] = Field(default_factory=list)

    assigned_region_id: UUID | None = None
    assigned_service_id: UUID | None = None

    @property
    def permission_set(self) -> set[str]:
        return {p.lower() for p in self.permissions}

    def has_role(self, *roles: str) -> bool:
        if not self.role:
            return False

        if self.role == UserRole.SUPERADMIN.value:
            return True

        normalized_required = {str(r).lower() for r in roles}
        return self.role.lower() in normalized_required

    def has_permission(self, *perms: str, any_of: bool = False) -> bool:
        if not perms:
            return False

        if not self.role:
            return False

        if self.role == UserRole.SUPERADMIN.value:
            return True

        required = {str(p).lower() for p in perms}
        user_perms = self.permission_set

        if any_of:
            return not user_perms.isdisjoint(required)
        return required.issubset(user_perms)


class TokenPayloadSchema(BaseSchema):
    sub: UUID
    jti: UUID
    exp: int
    iat: int
    type: str
    iss: str | None = None
    aud: str | None = None
    session_id: UUID | None = None


class TokenPairSchema(BaseSchema):
    access_token: str
    refresh_token: str


class LoginRequestSchema(BaseSchema):
    login: str
    password: str


class TokenResponseSchema(BaseSchema):
    access_token: str
    refresh_token: str


class RefreshRequestSchema(BaseSchema):
    refresh_token: str
