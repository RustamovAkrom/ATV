from datetime import datetime
from decimal import Decimal
from typing import Any

from core.exceptions.errors import ValidationError
from db.models.enums import UserRole
from schemas.analytics.common import AnalyticsFilters
from schemas.auth import CurrentUserSchema
from utils.analytics.aggregation_utils import safe_money
from utils.helpers import utc_now


class BaseAnalyticsService:
    """Base service for analytics business rules.

    Services own validation, privacy filtering, DTO conversion helpers, and
    calculations that are not better handled by the database.
    """

    @staticmethod
    def validate_filters(filters: AnalyticsFilters, user: CurrentUserSchema) -> None:
        """Validate date and scope filters for the current user.

        Args:
            filters: Region, service, and date filters requested by the client.
            user: Authenticated user used for scope checks.

        Raises:
            ValidationError: If date or scope filters are invalid.
        """
        if (
            filters.date_from
            and filters.date_to
            and filters.date_from > filters.date_to
        ):
            raise ValidationError("date_from cannot be greater than date_to")

        if (
            user.assigned_department_id
            and filters.department_id
            and filters.department_id != user.assigned_department_id
        ):
            raise ValidationError("department_id is outside your scope")

        if (
            user.assigned_region_id
            and filters.region_id
            and filters.region_id != user.assigned_region_id
        ):
            raise ValidationError("region_id is outside your scope")

        if (
            user.assigned_service_id
            and filters.service_id
            and filters.service_id != user.assigned_service_id
        ):
            raise ValidationError("service_id is outside your scope")

    @staticmethod
    def filter_email(email: str, user: CurrentUserSchema) -> str:
        """Hide email addresses from non-admin analytics viewers."""
        if user.has_role(UserRole.ADMIN.value, UserRole.SUPERADMIN.value):
            return email
        return ""

    @staticmethod
    def calculate_duration_days(
        start: datetime, end: datetime | None
    ) -> Decimal | None:
        """Calculate duration in days between two datetimes."""
        if end is None:
            return None
        duration = end - start
        return Decimal(duration.total_seconds() / 86400)

    @staticmethod
    def format_duration(start: datetime, end: datetime | None) -> str:
        """Format a duration as a compact days/hours string."""
        effective_end = end or utc_now()
        duration = effective_end - start
        total_hours = int(duration.total_seconds() // 3600)
        days, hours = divmod(total_hours, 24)
        return f"{days}d {hours}h"

    @staticmethod
    def safe_money(value: Any) -> float:
        """Convert nullable numeric DB values to a frontend-safe float."""
        return safe_money(value)

    @staticmethod
    def to_distribution(
        rows: list,
        total: int,
        id_field: str = "id",
        name_field: str = "name",
        count_field: str = "asset_count",
    ):
        """Convert aggregate rows to ``DistributionSchema``."""
        from schemas.analytics.common import AggregationResultSchema, DistributionSchema

        items = []
        for row in rows:
            count = int(getattr(row, count_field, 0) or 0)
            label = str(
                getattr(row, name_field, None) or getattr(row, "status", "Unknown")
            )
            key = str(getattr(row, id_field, None) or getattr(row, "status", "unknown"))
            items.append(
                AggregationResultSchema(
                    key=key,
                    label=label,
                    count=count,
                    percentage=round((count / total * 100.0) if total else 0.0, 2),
                )
            )
        return DistributionSchema(
            labels=[item.label for item in items],
            values=[item.count for item in items],
            items=items,
        )
