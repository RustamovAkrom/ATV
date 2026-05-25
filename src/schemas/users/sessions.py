from datetime import datetime
from uuid import UUID

from schemas.base import BaseSchema


class SessionOutSchema(BaseSchema):
    id: UUID
    ip_address: str | None
    user_agent: str | None
    device_id: str | None

    is_revoked: bool
    is_active: bool

    created_at: datetime
    expires_at: datetime


class CleanupResponseSchema(BaseSchema):
    deleted: int
    message: str = "Old sessions removed"
