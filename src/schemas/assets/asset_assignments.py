from datetime import datetime
from uuid import UUID

from schemas.base import BaseRequestSchema


class AssetAssignmentRequest(BaseRequestSchema):
    user_id: UUID

class AssetReassignmentRequest(BaseRequestSchema):
    new_user_id: UUID

class AssetAssignmentActionSchema(BaseRequestSchema):
    asset_id: UUID
    user_id: UUID | None
    assigned_at: datetime | None = None
    unassigned_at: datetime | None = None
