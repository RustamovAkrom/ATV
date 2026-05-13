from datetime import datetime
from uuid import UUID

from schemas.base import BaseSchema


class AssetAssignmentRequest(BaseSchema):
    user_id: UUID


class AssetReassignmentRequest(BaseSchema):
    new_user_id: UUID


class AssetAssignmentActionSchema(BaseSchema):
    asset_id: UUID
    user_id: UUID | None
    assigned_at: datetime | None = None
    unassigned_at: datetime | None = None
