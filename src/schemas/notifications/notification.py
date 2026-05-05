from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationSchema(BaseModel):
    id: UUID
    type: str
    title: str
    message: str
    data: dict
    is_read: bool
    created_at: datetime
    read_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class NotificationCreate(BaseModel):
    user_id: UUID
    type: str
    title: str
    message: str
    data: dict = {}


class NotificationFilter(BaseModel):
    is_read: bool | None = None


class UnreadCountResponseSchema(BaseModel):
    count: int
    model_config = ConfigDict(from_attributes=True)
