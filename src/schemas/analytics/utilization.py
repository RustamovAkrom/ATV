from schemas.base import BaseResponseSchema


class UtilizationEmployeeSchema(BaseResponseSchema):
    user_id: str
    user_name: str
    asset_count: int


class UtilizationServiceSchema(BaseResponseSchema):
    service_id: str
    service_name: str
    asset_count: int


class UtilizationRegionLoadSchema(BaseResponseSchema):
    region_id: str
    region_name: str
    asset_count: int
    employee_count: int
    load_ratio: float


class UtilizationAnalyticsDataSchema(BaseResponseSchema):
    assets_per_employee: list[UtilizationEmployeeSchema]
    assets_per_service: list[UtilizationServiceSchema]
    overloaded_regions: list[UtilizationRegionLoadSchema]
    underutilized_regions: list[UtilizationRegionLoadSchema]
