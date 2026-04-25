from repositories.analytics.forecast_analytics_repo import ForecastAnalyticsRepository
from schemas.analytics.forecast import ForecastPointOut, ForecastSeriesOut
from schemas.analytics.trends import TrendInterval
from services.analytics.trend_analytics_service import TrendAnalyticsService


class ForecastAnalyticsService:
    def __init__(self, repo: ForecastAnalyticsRepository):
        self.repo = repo
        self.trend_service = TrendAnalyticsService(repo)

    @staticmethod
    def _moving_average(values: list[int], window: int) -> float:
        if not values:
            return 0.0
        relevant = values[-window:]
        return float(sum(relevant) / len(relevant))

    async def repair_forecast(
        self, interval: TrendInterval, periods: int, basis_window: int
    ):
        series = await self.trend_service.repair_trends(interval, periods)
        values = [point.value for point in series.points]
        moving_average = self._moving_average(values, basis_window)
        return ForecastSeriesOut(
            interval=interval,
            basis_window=basis_window,
            forecast_periods=periods,
            moving_average=moving_average,
            points=[
                ForecastPointOut(period_index=index + 1, forecast_value=moving_average)
                for index in range(periods)
            ],
        )

    async def failure_forecast(
        self, interval: TrendInterval, periods: int, basis_window: int
    ):
        series = await self.trend_service.repair_trends(interval, periods)
        values = [point.value for point in series.points]
        moving_average = self._moving_average(values, basis_window)
        return ForecastSeriesOut(
            interval=interval,
            basis_window=basis_window,
            forecast_periods=periods,
            moving_average=moving_average,
            points=[
                ForecastPointOut(period_index=index + 1, forecast_value=moving_average)
                for index in range(periods)
            ],
        )
