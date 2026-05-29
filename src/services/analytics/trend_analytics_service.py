from datetime import datetime, timedelta

from repositories.analytics.trend_analytics_repo import TrendAnalyticsRepository
from schemas.analytics.trends import (
    RepairTrendPointOut,
    RepairTrendSeriesOut,
    TrendInterval,
    TrendPointOut,
    TrendSeriesOut,
)
from utils.analytics.date_utils import (
    AnalyticsPeriod,
    advance_period,
    align_period_start,
)
from utils.helpers import utc_now


def _to_analytics_period(interval: TrendInterval) -> AnalyticsPeriod:
    if interval == TrendInterval.MONTHLY:
        return AnalyticsPeriod.MONTH
    if interval == TrendInterval.WEEKLY:
        return AnalyticsPeriod.WEEK
    return AnalyticsPeriod.DAY


class TrendAnalyticsService:
    def __init__(self, repo: TrendAnalyticsRepository):
        self.repo = repo

    @staticmethod
    def _align_start(dt: datetime, interval: TrendInterval) -> datetime:
        return align_period_start(dt, _to_analytics_period(interval))

    @staticmethod
    def _advance_bucket(dt: datetime, interval: TrendInterval) -> datetime:
        return advance_period(dt, _to_analytics_period(interval))

    def _resolve_period(self, interval: TrendInterval, periods: int):
        step_days = (
            1
            if interval == TrendInterval.DAILY
            else 7
            if interval == TrendInterval.WEEKLY
            else 30
        )
        end = utc_now()
        start = self._align_start(
            end - timedelta(days=step_days * max(periods - 1, 0)), interval
        )
        return start, end, step_days

    def _normalize_points(
        self, rows, interval: TrendInterval, periods: int, with_cost: bool = False
    ):
        start, _, _ = self._resolve_period(interval, periods)
        lookup = {row.bucket_start: row for row in rows}
        points = []
        current = start

        for _ in range(periods):
            bucket_start = self._align_start(current, interval)
            row = lookup.get(bucket_start)
            bucket_end = self._advance_bucket(bucket_start, interval)

            if with_cost:
                points.append(
                    RepairTrendPointOut(
                        bucket_start=bucket_start,
                        bucket_end=bucket_end,
                        value=int(row.value if row else 0),
                        total_cost=float(row.total_cost if row else 0),
                    )
                )
            else:
                points.append(
                    TrendPointOut(
                        bucket_start=bucket_start,
                        bucket_end=bucket_end,
                        value=int(row.value if row else 0),
                    )
                )
            current = bucket_end

        return points

    async def assignment_trends(
        self, interval: TrendInterval, periods: int
    ) -> TrendSeriesOut:
        start, end, _ = self._resolve_period(interval, periods)
        rows = await self.repo.assignment_counts(interval.value, start, end)
        return TrendSeriesOut(
            interval=interval, points=self._normalize_points(rows, interval, periods)
        )

    async def transfer_trends(
        self, interval: TrendInterval, periods: int
    ) -> TrendSeriesOut:
        start, end, _ = self._resolve_period(interval, periods)
        rows = await self.repo.transfer_counts(interval.value, start, end)
        return TrendSeriesOut(
            interval=interval, points=self._normalize_points(rows, interval, periods)
        )

    async def repair_trends(
        self, interval: TrendInterval, periods: int
    ) -> RepairTrendSeriesOut:
        start, end, _ = self._resolve_period(interval, periods)
        rows = await self.repo.repair_counts(interval.value, start, end)
        return RepairTrendSeriesOut(
            interval=interval,
            points=self._normalize_points(rows, interval, periods, with_cost=True),
        )
