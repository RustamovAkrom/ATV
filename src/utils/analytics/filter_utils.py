from uuid import UUID

from core.config import get_settings

settings = get_settings()


def sanitize_search(value: str | None) -> str | None:
    """Normalize user-provided search text for safe ``ILIKE`` usage.

    SQL wildcard characters are replaced with spaces so callers can still bind the
    returned text as a parameter without widening the search unexpectedly.
    """
    if value is None:
        return None
    cleaned = " ".join(
        value.replace("%", " ").replace("_", " ").replace("*", " ").split()
    )
    return cleaned[: settings.ANALYTICS_SEARCH_MAX_LENGTH] if cleaned else None


def scoped_region_service_filters(
    asset_table,
    region_id: UUID | None = None,
    service_id: UUID | None = None,
    scoped_region_id: UUID | None = None,
    scoped_service_id: UUID | None = None,
) -> list:
    """Build SQLAlchemy filters for region/service scope."""
    filters = []
    target_region_id = scoped_region_id or region_id
    target_service_id = scoped_service_id or service_id
    if target_region_id:
        filters.append(asset_table.region_id == target_region_id)
    if target_service_id:
        filters.append(asset_table.service_id == target_service_id)
    return filters
