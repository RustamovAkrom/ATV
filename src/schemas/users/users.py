from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from db.models.enums import UserStatus


class UserCreateSchema(BaseModel):
    login: str
    email: EmailStr
    phone: str
    password: str
    first_name: str | None
    last_name: str | None
    status: UserStatus | None
    role_id: UUID


class UserUpdateSchema(BaseModel):
    first_name: str | None
    last_name: str | None
    phone: str | None


class AdminUserUpdateSchema(BaseModel):
    role_id: UUID | None
    status: str | None


class ChangePasswordRequestSchema(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


class UserOutSchema(BaseModel):
    id: UUID
    login: str
    email: str
    phone: str
    role: str | None
    permissions: list[str]
    first_name: str | None
    last_name: str | None
    status: UserStatus
    created_at: datetime | None
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
