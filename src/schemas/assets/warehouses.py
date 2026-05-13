from uuid import UUID

from schemas.base import BaseSchema


class WarehouseMoveRequest(BaseSchema):
    warehouse_id: UUID
