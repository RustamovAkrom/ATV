from pydantic import BaseModel


class UtilizationEmployeeSchema(BaseModel):
    user_id: str
    user_name: str
    asset_count: int


class UtilizationServiceSchema(BaseModel):
    service_id: str
    service_name: str
    asset_count: int


class UtilizationRegionLoadSchema(BaseModel):
    region_id: str
    region_name: str
    asset_count: int
    employee_count: int
    load_ratio: float


class UtilizationAnalyticsDataSchema(BaseModel):
    assets_per_employee: list[UtilizationEmployeeSchema]
    assets_per_service: list[UtilizationServiceSchema]
    overloaded_regions: list[UtilizationRegionLoadSchema]
    underutilized_regions: list[UtilizationRegionLoadSchema]
