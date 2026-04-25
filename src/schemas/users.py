from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from db.models.enums import UserStatus


class UserCreateSchema(BaseModel):
    login: str
    email: EmailStr
    phone: str
    password: str
    first_name: Optional[str]
    last_name: Optional[str]
    status: Optional[UserStatus]
    role_id: UUID


class UserUpdateSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]


class AdminUserUpdateSchema(BaseModel):
    role_id: Optional[UUID]
    status: Optional[str]


class ChangePasswordRequestSchema(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


class UserOutSchema(BaseModel):
    id: UUID
    login: str
    email: str
    phone: str
    role: str
    permissions: List[str]
    first_name: Optional[str]
    last_name: Optional[str]
    status: UserStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
