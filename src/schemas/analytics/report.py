from schemas.analytics.common import KPIResponseSchema
from schemas.base import BaseResponseSchema


class ReportDataSchema(BaseResponseSchema):
    summary: dict
    breakdowns: dict
    trends: dict


class OverviewDataSchema(BaseResponseSchema):
    kpis: list[KPIResponseSchema]
    breakdowns: dict
    trends: dict
