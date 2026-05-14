# services/analytics/asset_transfer_analytics_service.py

from decimal import Decimal
from uuid import UUID

from db.models.assets.asset_transfer import AssetTransfer
from db.models.enums import TransferStatus
from repositories.analytics.asset_transfer_analytics_repo import (
    AssetTransferAnalyticsRepository,
)
from schemas.analytics.asset_transfer_analytics import (
    AssetTransferFilterInput,
    AssetTransferHistory,
    AssetTransferOut,
    AssetTransferPageOut,
    BottleneckReportOut,
    TransferBottleneck,
    TransferHistoryEntry,
    TransferMetrics,
    TransferStatusBreakdown,
    WarehouseTransferMetrics,
)
from schemas.pagination import PageOutSchema, PaginationParamsSchema
from utils.helpers import utc_now


class AssetTransferAnalyticsService:
    """Service for transfer analytics."""

    def __init__(self, repo: AssetTransferAnalyticsRepository):
        self.repo = repo

    async def list_transfers(
        self,
        filters: AssetTransferFilterInput,
        pagination: PaginationParamsSchema,
    ) -> AssetTransferPageOut:
        """List transfers with pagination."""
        transfers, total = await self.repo.list_transfers(filters, pagination)

        items = [self._to_transfer_out(t) for t in transfers]

        return PageOutSchema(
            items=items,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def get_metrics(self, filters: AssetTransferFilterInput) -> TransferMetrics:
        return await self.get_transfer_metrics(filters)

    async def list_pending_transfers(
        self,
        pagination: PaginationParamsSchema,
    ) -> AssetTransferPageOut:
        """List pending transfers."""
        transfers, total = await self.repo.list_pending_transfers(pagination)

        items = [self._to_transfer_out(t) for t in transfers]

        return PageOutSchema(
            items=items,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def get_asset_transfer_history(self, asset_id: UUID) -> AssetTransferHistory:
        """Get transfer history for an asset."""
        transfers = await self.repo.get_transfer_history_for_asset(asset_id)

        # Get asset info from first transfer if available
        asset = transfers[0].asset if transfers else None

        # Calculate status breakdown
        completed = sum(1 for t in transfers if t.status == TransferStatus.COMPLETED)
        pending = sum(1 for t in transfers if t.status == TransferStatus.PENDING)
        cancelled = sum(1 for t in transfers if t.status == TransferStatus.CANCELLED)

        # Build history entries
        history = [
            TransferHistoryEntry(
                transfer_id=t.id,
                sequence=i + 1,
                status=t.status.value,
                from_location=(
                    t.from_warehouse.name
                    if t.from_warehouse
                    else (t.from_service.name if t.from_service else None)
                ),
                to_location=(
                    t.to_warehouse.name
                    if t.to_warehouse
                    else (t.to_service.name if t.to_service else None)
                ),
                created_at=t.created_at,
                transferred_at=t.transferred_at,
                created_by_name=t.created_by.full_name if t.created_by else "Unknown",
                duration_days=self._calculate_duration_days(
                    t.created_at, t.transferred_at
                ),
            )
            for i, t in enumerate(transfers)
        ]

        return AssetTransferHistory(
            asset_id=asset_id,
            asset_name=asset.name if asset else "Unknown",
            total_transfers=len(transfers),
            completed_transfers=completed,
            pending_transfers=pending,
            cancelled_transfers=cancelled,
            history=history,
        )

    async def get_transfer_metrics(
        self, filters: AssetTransferFilterInput
    ) -> TransferMetrics:
        """Get aggregated transfer metrics."""
        agg_dict = await self.repo.get_transfer_aggregates(filters)

        # Calculate percentages for status breakdown
        total = agg_dict["total_transfers"] or 0
        status_breakdown = [
            TransferStatusBreakdown(
                status="completed",
                count=agg_dict["completed_transfers"],
                percentage=(
                    Decimal(100 * agg_dict["completed_transfers"] / total)
                    if total > 0
                    else Decimal(0)
                ),
                average_pending_days=None,
            ),
            TransferStatusBreakdown(
                status="pending",
                count=agg_dict["pending_transfers"],
                percentage=(
                    Decimal(100 * agg_dict["pending_transfers"] / total)
                    if total > 0
                    else Decimal(0)
                ),
                average_pending_days=Decimal(0),  # Could calculate separately if needed
            ),
            TransferStatusBreakdown(
                status="cancelled",
                count=agg_dict["cancelled_transfers"],
                percentage=(
                    Decimal(100 * agg_dict["cancelled_transfers"] / total)
                    if total > 0
                    else Decimal(0)
                ),
                average_pending_days=None,
            ),
        ]

        return TransferMetrics(
            total_transfers=agg_dict["total_transfers"],
            completed_transfers=agg_dict["completed_transfers"],
            pending_transfers=agg_dict["pending_transfers"],
            cancelled_transfers=agg_dict["cancelled_transfers"],
            average_completion_time_days=agg_dict["average_completion_time_days"],
            longest_completion_time_days=agg_dict["longest_completion_time_days"],
            shortest_completion_time_days=agg_dict["shortest_completion_time_days"],
            oldest_pending_transfer_days=agg_dict["oldest_pending_transfer_days"],
            oldest_pending_transfer_id=agg_dict["oldest_pending_transfer_id"],
            transfers_pending_over_7_days=agg_dict["transfers_pending_over_7_days"],
            transfers_pending_over_30_days=agg_dict["transfers_pending_over_30_days"],
            status_breakdown=status_breakdown,
        )

    async def get_bottleneck_report(
        self,
        critical_days: int = 30,
        warning_days: int = 7,
    ) -> BottleneckReportOut:
        """Get transfer bottleneck report."""
        bottlenecks_dict = await self.repo.get_bottlenecks(critical_days, warning_days)

        critical_bottlenecks = [
            self._to_bottleneck(t) for t in bottlenecks_dict["critical"]
        ]

        warning_bottlenecks = [
            self._to_bottleneck(t) for t in bottlenecks_dict["warning"]
        ]

        return BottleneckReportOut(
            total_bottlenecks=len(critical_bottlenecks) + len(warning_bottlenecks),
            critical_bottlenecks=critical_bottlenecks,
            warning_bottlenecks=warning_bottlenecks,
        )

    async def get_warehouse_metrics(
        self, warehouse_id: UUID
    ) -> WarehouseTransferMetrics:
        """Get transfer metrics for a warehouse."""
        metrics_dict = await self.repo.get_warehouse_transfer_metrics(warehouse_id)

        return WarehouseTransferMetrics(**metrics_dict)

    def _to_transfer_out(self, transfer: AssetTransfer) -> AssetTransferOut:
        """Convert transfer model to output schema."""
        return AssetTransferOut(
            id=transfer.id,
            asset_id=transfer.asset_id,
            asset_name=transfer.asset.name if transfer.asset else "Unknown",
            asset_tag=transfer.asset.asset_tag if transfer.asset else None,
            status=transfer.status.value,
            from_warehouse_name=(
                transfer.from_warehouse.name if transfer.from_warehouse else None
            ),
            to_warehouse_name=(
                transfer.to_warehouse.name if transfer.to_warehouse else None
            ),
            from_service_name=(
                transfer.from_service.name if transfer.from_service else None
            ),
            to_service_name=transfer.to_service.name if transfer.to_service else None,
            created_by_id=transfer.created_by_id,
            created_by_name=(
                transfer.created_by.full_name if transfer.created_by else "Unknown"
            ),
            created_at=transfer.created_at,
            received_by_id=transfer.received_by_id,
            received_by_name=(
                transfer.received_by.full_name if transfer.received_by else None
            ),
            transferred_at=transfer.transferred_at,
            comment=transfer.comment,
        )

    def _to_bottleneck(self, transfer) -> TransferBottleneck:
        """Convert transfer to bottleneck entry."""
        pending_days = (utc_now() - transfer.created_at).days

        return TransferBottleneck(
            transfer_id=transfer.id,
            asset_name=transfer.asset.name if transfer.asset else "Unknown",
            asset_tag=transfer.asset.asset_tag if transfer.asset else None,
            status=transfer.status.value,
            pending_days=pending_days,
            created_by_name=(
                transfer.created_by.full_name if transfer.created_by else "Unknown"
            ),
            from_location=(
                transfer.from_warehouse.name
                if transfer.from_warehouse
                else (transfer.from_service.name if transfer.from_service else None)
            ),
            to_location=(
                transfer.to_warehouse.name
                if transfer.to_warehouse
                else (transfer.to_service.name if transfer.to_service else None)
            ),
            created_at=transfer.created_at,
        )

    @staticmethod
    def _calculate_duration_days(start, end) -> Decimal | None:
        """Calculate duration in days."""
        if end is None:
            return None
        duration = end - start
        return Decimal(duration.total_seconds() / 86400)
