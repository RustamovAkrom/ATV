from uuid import UUID

from pydantic import BaseModel


class RegionMetrics(BaseModel):
    total: int
    active: int
    inactive: int
    repair: int


class RegionDistributionOut(BaseModel):
    region_id: UUID
    region_name: str

    metrics: RegionMetrics
    health_score: float
    latitude: float | None = None
    longitude: float | None = None
    geojson: dict | None = None
