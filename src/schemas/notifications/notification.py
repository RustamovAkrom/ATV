from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict

from schemas.base import BaseRequestSchema, BaseSchema


class NotificationSchema(BaseSchema):
    id: UUID
    type: str
    title: str
    message: str
    data: dict
    is_read: bool
    created_at: datetime
    read_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class NotificationCreate(BaseRequestSchema):
    user_id: UUID
    type: str
    title: str
    message: str
    data: dict = {}

class NotificationFilter(BaseRequestSchema):
    is_read: bool | None = None

class UnreadCountResponseSchema(BaseSchema):
    count: int
    model_config = ConfigDict(from_attributes=True)
