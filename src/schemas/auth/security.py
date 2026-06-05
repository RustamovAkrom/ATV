import re

from pydantic import field_validator

from schemas.base import BaseRequestSchema


class ResetPasswordRequestSchema(BaseRequestSchema):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password too short")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain uppercase")

        if not re.search(r"[a-z]", v):
            raise ValueError("Must contain lowercase")

        if not re.search(r"\d", v):
            raise ValueError("Must contain digit")

        return v


class ForgotPasswordRequestSchema(BaseRequestSchema):
    login: str
