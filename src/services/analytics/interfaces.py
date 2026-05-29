from collections.abc import Awaitable, Callable
from datetime import date, datetime
from typing import Any, Protocol, TypeVar
from uuid import UUID

from schemas.pagination import PaginationParamsSchema

T = TypeVar("T")


class IDateFilterable(Protocol):
    """Interface for components that can build date filters."""

    @staticmethod
    def date_filters(
        table_column: Any,
        date_from: date | datetime | None = None,
        date_to: date | datetime | None = None,
    ) -> list:
        """Build filters for a date range."""
        ...


class IRegionFilterable(Protocol):
    """Interface for components that can build region/service scope filters."""

    @staticmethod
    def scope_filters(
        asset_table: Any,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        scoped_region_id: UUID | None = None,
        scoped_service_id: UUID | None = None,
    ) -> list:
        """Build region and service filters."""
        ...


class IAggregatable(Protocol):
    """Interface for analytics repositories that expose aggregate counts."""

    async def get_count(self, table: Any, filters: list | None = None) -> int:
        """Return a filtered row count."""
        ...


class IPaginatable(Protocol):
    """Interface for repositories that apply pagination."""

    async def execute_with_pagination(
        self,
        query: Any,
        pagination: PaginationParamsSchema,
        order_by: Any | None = None,
    ) -> tuple[Any, int]:
        """Execute a paginated SQLAlchemy query."""
        ...


class IExportable(Protocol):
    """Interface for services that can export analytics output."""

    async def export(self, *args: Any, **kwargs: Any) -> bytes:
        """Export analytics data as bytes."""
        ...


class ICacheable(Protocol):
    """Interface for services that cache expensive analytics work."""

    async def cached(
        self,
        key: str,
        loader: Callable[[], Awaitable[T]],
        ttl_seconds: int,
    ) -> T:
        """Return cached data or load and store it."""
        ...
