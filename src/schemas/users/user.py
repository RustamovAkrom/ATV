from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from db.models.enums import UserStatus, UserGender, EmploymentType, UserLanguage


class UserCreateSchema(BaseModel):
    login: str
    email: EmailStr
    phone: str
    password: str
    first_name: str | None
    last_name: str | None
    status: UserStatus | None
    role_id: UUID
    # new attributes
    position: str | None = None
    department: str | None = None
    employment_type: EmploymentType | None = None
    date_of_birth: date | None = None
    gender: UserGender | None = None
    badge_number: str | None = None
    passport_number: str | None = None
    hired_at: date | None = None
    language: UserLanguage | None = None
    timezone: str | None = "Asia/Tashkent"


class UserUpdateSchema(BaseModel):
    first_name: str | None
    last_name: str | None
    phone: str | None
    date_of_birth: date | None
    gender: UserGender | None
    badge_number: str | None
    passport_number: str | None
    avatar_url: str | None
    # new attributes
    position: str | None = None
    department: str | None = None
    employment_type: EmploymentType | None = None
    hired_at: date | None = None
    language: UserLanguage | None = None
    timezone: str | None = None

class AdminUserUpdateSchema(BaseModel):
    role_id: UUID | None
    status: str | None
    # Admin can change this values
    assigned_region_id: UUID | None = None
    assigned_service_id: UUID | None = None
    position: str | None = None
    department: str | None = None
    employment_type: EmploymentType | None = None
    badge_number: str | None
    passport_number: str | None
    hired_at: date | None = None
    dismissed_at: date | None = None


class ChangePasswordRequestSchema(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


class UserAvatarUpdateSchema(BaseModel):
    avatar_url: str | None = Field(None, max_length=500)


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
    # new values
    position: str | None = None
    department: str | None = None
    employment_type: EmploymentType | None = None
    date_of_birth: date | None = None
    gender: UserGender | None = None
    badge_number: str | None = None
    passport_number: str | None = None
    avatar_url: str | None = None
    hired_at: date | None = None

    dismissed_at: date | None = None
    language: UserLanguage | None = None
    timezone: str | None = None
    last_login: datetime | None = None
    assigned_region_id: UUID | None = None
    assigned_service_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)
