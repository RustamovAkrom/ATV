import csv
import io
from collections.abc import Iterable
from typing import Any

from services.analytics.base_analytics_service import BaseAnalyticsService


class ExportAnalyticsService(BaseAnalyticsService):
    """Export analytics rows into lightweight report formats."""

    async def export_csv(
        self,
        rows: Iterable[dict[str, Any]],
        fieldnames: list[str],
    ) -> bytes:
        """Export dictionaries as UTF-8 CSV bytes.

        Args:
            rows: Iterable of flat dictionaries.
            fieldnames: Ordered CSV column names.

        Returns:
            UTF-8 encoded CSV content.
        """
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue().encode("utf-8")

    async def export(self, *args: Any, **kwargs: Any) -> bytes:
        """Protocol-compatible export entrypoint."""
        rows = list(kwargs.get("rows") or (args[0] if args else []))
        fieldnames = kwargs.get("fieldnames") or (list(rows[0].keys()) if rows else [])
        return await self.export_csv(rows, fieldnames)
