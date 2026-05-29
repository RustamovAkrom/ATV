from datetime import UTC, date, datetime, time, timedelta
from enum import StrEnum

from fastapi import HTTPException


class AnalyticsPeriod(StrEnum):
    """Supported calendar periods for analytics buckets."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


def parse_optional_datetime(value: str | None) -> datetime | None:
    """Parse an optional ISO 8601 datetime as UTC.

    Args:
        value: ISO 8601 datetime string or ``None``.

    Returns:
        Timezone-aware UTC datetime or ``None``.

    Raises:
        HTTPException: If the input cannot be parsed.
    """
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail="Invalid ISO 8601 datetime format"
        ) from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def normalize_date_start(value: date | datetime | None) -> datetime | None:
    """Normalize a date or datetime to a datetime at day start."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.min)


def normalize_date_end(value: date | datetime | None) -> datetime | None:
    """Normalize a date or datetime to a datetime at day end."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.max)


def align_period_start(value: datetime, period: AnalyticsPeriod) -> datetime:
    """Align a datetime to the beginning of a calendar period."""
    if period == AnalyticsPeriod.YEAR:
        return value.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    if period == AnalyticsPeriod.QUARTER:
        month = ((value.month - 1) // 3) * 3 + 1
        return value.replace(
            month=month, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    if period == AnalyticsPeriod.MONTH:
        return value.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if period == AnalyticsPeriod.WEEK:
        aligned = value - timedelta(days=value.weekday())
        return aligned.replace(hour=0, minute=0, second=0, microsecond=0)
    return value.replace(hour=0, minute=0, second=0, microsecond=0)


def advance_period(value: datetime, period: AnalyticsPeriod) -> datetime:
    """Advance a datetime by one analytics period."""
    if period == AnalyticsPeriod.YEAR:
        return value.replace(year=value.year + 1, month=1, day=1)
    if period == AnalyticsPeriod.QUARTER:
        year = value.year + ((value.month + 2) // 12)
        month = ((value.month + 2) % 12) + 1
        return value.replace(year=year, month=month, day=1)
    if period == AnalyticsPeriod.MONTH:
        year = value.year + (1 if value.month == 12 else 0)
        month = 1 if value.month == 12 else value.month + 1
        return value.replace(year=year, month=month, day=1)
    if period == AnalyticsPeriod.WEEK:
        return value + timedelta(days=7)
    return value + timedelta(days=1)
