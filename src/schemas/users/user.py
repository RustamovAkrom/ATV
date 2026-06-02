from datetime import date, datetime
from uuid import UUID

from pydantic import ConfigDict, EmailStr, Field, field_validator

from db.models.enums import EmploymentType, UserGender, UserLanguage, UserStatus
from schemas.base import BaseRequestSchema, TimestampSchema


class UserCreateSchema(BaseRequestSchema):
    login: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=6, max_length=100)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    status: UserStatus | None = UserStatus.ACTIVE
    role_id: UUID

    # new attributes
    position: str | None = Field(None, max_length=255)
    department: str | None = Field(None, max_length=255)
    employment_type: EmploymentType | None = None
    date_of_birth: date | None = Field(None, description="Date of birth")
    gender: UserGender | None = None
    badge_number: str | None = Field(None, max_length=50)
    passport_number: str | None = Field(None, max_length=50)
    hired_at: date | None = Field(None, description="Employment start date")
    language: UserLanguage | None = UserLanguage.UZ
    timezone: str | None = Field("Asia/Tashkent", max_length=50)

class UserUpdateSchema(BaseRequestSchema):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, min_length=7, max_length=20)
    date_of_birth: date | None = None
    gender: UserGender | None = None
    badge_number: str | None = Field(None, max_length=50)
    passport_number: str | None = Field(None, max_length=50)
    avatar_url: str | None = Field(None, max_length=500)

    # new attributes
    position: str | None = Field(None, max_length=255)
    department: str | None = Field(None, max_length=255)
    employment_type: EmploymentType | None = None
    hired_at: date | None = None
    language: UserLanguage | None = None
    timezone: str | None = Field(None, max_length=50)

class AdminUserUpdateSchema(BaseRequestSchema):
    role_id: UUID | None
    status: str | None
    # Admin can change this values
    assigned_region_id: UUID | None = None
    assigned_service_id: UUID | None = None
    position: str | None = Field(None, max_length=255)
    department: str | None = Field(None, max_length=255)
    employment_type: EmploymentType | None = None
    badge_number: str | None = Field(None, max_length=50)
    passport_number: str | None = Field(None, max_length=50)
    hired_at: date | None = None
    dismissed_at: date | None = None

class ChangePasswordRequestSchema(BaseRequestSchema):
    old_password: str
    new_password: str = Field(min_length=6)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) > 6:
            raise ValueError("Password must be at least 5 charecters")
        return v

class UserAvatarUpdateSchema(BaseRequestSchema):
    avatar_url: str | None = Field(None, max_length=500)

class UserOutSchema(TimestampSchema):
    id: UUID
    login: str
    email: str
    phone: str
    role: str | None
    first_name: str | None
    last_name: str | None
    status: UserStatus

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
