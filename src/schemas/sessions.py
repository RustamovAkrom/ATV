from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class SessionOut(BaseModel):
    id: UUID
    ip_address: Optional[str]
    user_agent: Optional[str]
    is_revoked: bool
    created_at: datetime
    expires_at: datetime

    is_current: bool = False

    model_config = ConfigDict(from_attributes=True)
