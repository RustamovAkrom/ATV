from uuid import UUID

from pydantic import Field

from schemas.base import BaseRequestSchema, BaseSchema


class StockMovementCreateSchema(BaseRequestSchema):
    quantity: int = Field(gt=0, le=1_000_000)
    reference_type: str = Field(default="manual", max_length=50)
    reference_id: UUID | None = None


class StockMovementOutSchema(BaseSchema):
    id: UUID
    warehouse_id: UUID
    part_id: UUID
    movement_type: str
    quantity: int
    reference_type: str
    reference_id: UUID | None
    moved_by: UUID
    moved_at: str
