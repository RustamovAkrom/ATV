from datetime import datetime, timedelta

from repositories.analytics.trend_analytics_repo import TrendAnalyticsRepository
from schemas.analytics.trends import (
    RepairTrendPointOut,
    RepairTrendSeriesOut,
    TrendInterval,
    TrendPointOut,
    TrendSeriesOut,
)
from utils.helpers import utc_now


class TrendAnalyticsService:
    def __init__(self, repo: TrendAnalyticsRepository):
        self.repo = repo

    @staticmethod
    def _align_start(dt: datetime, interval: TrendInterval) -> datetime:
        if interval == TrendInterval.MONTHLY:
            return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if interval == TrendInterval.WEEKLY:
            aligned = dt - timedelta(days=dt.weekday())
            return aligned.replace(hour=0, minute=0, second=0, microsecond=0)
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def _advance_bucket(dt: datetime, interval: TrendInterval) -> datetime:
        if interval == TrendInterval.MONTHLY:
            year = dt.year + (1 if dt.month == 12 else 0)
            month = 1 if dt.month == 12 else dt.month + 1
            return dt.replace(year=year, month=month, day=1)
        if interval == TrendInterval.WEEKLY:
            return dt + timedelta(days=7)
        return dt + timedelta(days=1)

    @staticmethod
    def _resolve_period(interval: TrendInterval, periods: int):
        step_days = (
            1
            if interval == TrendInterval.DAILY
            else 7 if interval == TrendInterval.WEEKLY else 30
        )
        end = utc_now()
        start = TrendAnalyticsService._align_start(
            end - timedelta(days=step_days * max(periods - 1, 0)),
            interval,
        )
        return start, end, step_days

    @staticmethod
    def _normalize_points(
        rows, interval: TrendInterval, periods: int, with_cost: bool = False
    ):
        start, _, step_days = TrendAnalyticsService._resolve_period(interval, periods)
        lookup = {row.bucket_start: row for row in rows}
        points = []
        current = start
        for _ in range(periods):
            bucket_start = TrendAnalyticsService._align_start(current, interval)
            row = lookup.get(bucket_start)
            bucket_end = TrendAnalyticsService._advance_bucket(bucket_start, interval)
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

    async def assignment_trends(self, interval: TrendInterval, periods: int):
        start, end, _ = self._resolve_period(interval, periods)
        rows = await self.repo.assignment_counts(interval.value, start, end)
        return TrendSeriesOut(
            interval=interval,
            points=self._normalize_points(rows, interval, periods),
        )

    async def transfer_trends(self, interval: TrendInterval, periods: int):
        start, end, _ = self._resolve_period(interval, periods)
        rows = await self.repo.transfer_counts(interval.value, start, end)
        return TrendSeriesOut(
            interval=interval,
            points=self._normalize_points(rows, interval, periods),
        )

    async def repair_trends(self, interval: TrendInterval, periods: int):
        start, end, _ = self._resolve_period(interval, periods)
        rows = await self.repo.repair_counts(interval.value, start, end)
        return RepairTrendSeriesOut(
            interval=interval,
            points=self._normalize_points(rows, interval, periods, with_cost=True),
        )
