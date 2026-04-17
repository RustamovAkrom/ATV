from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from typing import Optional, List


class UserCreate(BaseModel):
    login: str
    email: EmailStr
    phone: str
    password: str

    first_name: Optional[str]
    last_name: Optional[str]

    role_id: UUID


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]


class AdminUserUpdate(BaseModel):
    role_id: Optional[UUID]
    status: Optional[str]


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


class UserOut(BaseModel):
    id: UUID
    login: str
    email: str
    phone: str
    role: str
    permissions: List[str]
    model_config = ConfigDict(from_attributes=True)
