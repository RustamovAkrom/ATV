from pydantic import BaseModel

from schemas.analytics.trends import TrendInterval


class ForecastPointOut(BaseModel):
    period_index: int
    forecast_value: float


class ForecastSeriesOut(BaseModel):
    interval: TrendInterval
    basis_window: int
    forecast_periods: int
    moving_average: float
    points: list[ForecastPointOut]

