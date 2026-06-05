from datetime import datetime
from uuid import UUID

from pydantic import Field, model_validator

from db.models.enums import TransferStatus
from schemas.base import BaseRequestSchema, BaseSchema


class AssetTransferCreate(BaseRequestSchema):
    from_warehouse_id: UUID | None = Field(None, description="Source warehouse")
    to_warehouse_id: UUID | None = None
    to_service_id: UUID | None = None
    comment: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_destination(self):
        if self.to_warehouse_id is None and self.to_service_id is None:
            raise ValueError("Transfer requires a target warehouse or service")

        if self.to_warehouse_id is not None and self.to_service_id is not None:
            raise ValueError("Transfer cannot have both warehouse and service targets")
        return self


class AssetTransferDecision(BaseRequestSchema):
    comment: str | None = Field(default=None, max_length=255)


class AssetTransferSchema(BaseSchema):
    id: UUID
    asset_id: UUID
    created_by_id: UUID
    received_by_id: UUID | None
    department_id: UUID | None
    status: TransferStatus
    from_warehouse_id: UUID | None
    to_warehouse_id: UUID | None
    from_service_id: UUID | None
    to_service_id: UUID | None
    comment: str | None
    transferred_at: datetime
    created_at: datetime
    updated_at: datetime
