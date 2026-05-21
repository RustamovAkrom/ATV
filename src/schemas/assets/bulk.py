from uuid import UUID

from pydantic import Field

from db.models.enums import AssetStatus
from schemas.assets.asset_transfers import AssetTransferCreate
from schemas.base import BaseSchema


class BulkAssignRequest(BaseSchema):
    asset_ids: list[UUID] = Field(min_length=1, max_length=100)
    user_id: UUID
    atomic: bool = False


class BulkTransferRequest(BaseSchema):
    asset_ids: list[UUID] = Field(min_length=1, max_length=100)
    transfer: AssetTransferCreate
    atomic: bool = False


class BulkStatusRequest(BaseSchema):
    asset_ids: list[UUID] = Field(min_length=1, max_length=100)
    status: AssetStatus
    atomic: bool = False


class BulkFailedItem(BaseSchema):
    id: UUID
    error: str


class BulkResult(BaseSchema):
    success: list[UUID]
    failed: list[BulkFailedItem]
