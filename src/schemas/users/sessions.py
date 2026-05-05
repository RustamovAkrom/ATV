from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SessionOutSchema(BaseModel):
    id: UUID
    ip_address: str | None
    user_agent: str | None
    device_id: str | None

    is_revoked: bool
    is_active: bool

    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CleanupResponseSchema(BaseModel):
    deleted: int
    message: str = "Old sessions removed"
    model_config = ConfigDict(from_attributes=True)
