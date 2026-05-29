from collections.abc import Iterable
from decimal import Decimal


def safe_money(value) -> float:
    """Convert nullable numeric DB values to a frontend-safe float."""
    return float(value or 0)


def percentage(part: int | Decimal | float, total: int | Decimal | float) -> Decimal:
    """Return a Decimal percentage guarded against division by zero."""
    if not total:
        return Decimal(0)
    return Decimal(100) * Decimal(part or 0) / Decimal(total)


def average(values: Iterable[int | float | Decimal]) -> float:
    """Calculate a numeric average for an iterable."""
    values = list(values)
    if not values:
        return 0.0
    return float(sum(values) / len(values))
