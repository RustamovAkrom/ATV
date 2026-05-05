from pydantic import BaseModel

from schemas.analytics.common import KPIResponseSchema


class ReportDataSchema(BaseModel):
    summary: dict
    breakdowns: dict
    trends: dict


class OverviewDataSchema(BaseModel):
    kpis: list[KPIResponseSchema]
    breakdowns: dict
    trends: dict
