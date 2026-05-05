from schemas.analytics.common import AnalyticsFilters
from schemas.auth import CurrentUserSchema
from core.exceptions.errors import ValidationError


def validate_filters(filters: AnalyticsFilters, user: CurrentUserSchema) -> None:
    if filters.date_from and filters.date_to and filters.date_from > filters.date_to:
        raise ValidationError("date_from cannot be greater than date_to")
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
