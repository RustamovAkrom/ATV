
from schemas.analytics.trends import TrendInterval
from schemas.base import BaseResponseSchema


class ForecastPointOut(BaseResponseSchema):
    period_index: int
    forecast_value: float

class ForecastSeriesOut(BaseResponseSchema):
    interval: TrendInterval
    basis_window: int
    forecast_periods: int
    moving_average: float
    points: list[ForecastPointOut]
