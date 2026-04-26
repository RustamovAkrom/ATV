from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AssetAssignmentRequest(BaseModel):
    user_id: UUID


class AssetReassignmentRequest(BaseModel):
    new_user_id: UUID


class AssetAssignmentActionSchema(BaseModel):
    asset_id: UUID
    user_id: UUID | None
    assigned_at: datetime | None = None
    unassigned_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
