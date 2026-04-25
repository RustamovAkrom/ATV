from uuid import UUID

from pydantic import BaseModel


class ServiceBreakdownOut(BaseModel):
    service_id: UUID
    service_name: str

    total_assets: int
    active_assets: int
    in_repair: int
