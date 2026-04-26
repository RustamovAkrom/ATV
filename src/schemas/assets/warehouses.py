from uuid import UUID

from pydantic import BaseModel


class WarehouseMoveRequest(BaseModel):
    warehouse_id: UUID
