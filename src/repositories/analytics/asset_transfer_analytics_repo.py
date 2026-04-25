# repositories/analytics/asset_transfer_analytics_repo.py

from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_transfer import AssetTransfer
from db.models.users.user import User
from db.models.warehouse.warehouse import Warehouse
from db.models.org.service import Service
from schemas.analytics.asset_transfer_analytics import AssetTransferFilterInput
from schemas.pagination import PaginationParams
from db.models.enums import TransferStatus
from utils.helpers import utc_now

class AssetTransferAnalyticsRepository:
    """Read-optimized repository for transfer analytics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _apply_filters(self, query, filters: AssetTransferFilterInput):
        """Apply filters to query."""
        filters = filters or AssetTransferFilterInput()

        if filters.asset_id:
            query = query.where(AssetTransfer.asset_id == filters.asset_id)

        if filters.created_by_id:
            query = query.where(AssetTransfer.created_by_id == filters.created_by_id)

        if filters.received_by_id:
            query = query.where(AssetTransfer.received_by_id == filters.received_by_id)

        if filters.from_warehouse_id:
            query = query.where(AssetTransfer.from_warehouse_id == filters.from_warehouse_id)

        if filters.to_warehouse_id:
            query = query.where(AssetTransfer.to_warehouse_id == filters.to_warehouse_id)

        if filters.from_service_id:
            query = query.where(AssetTransfer.from_service_id == filters.from_service_id)

        if filters.to_service_id:
            query = query.where(AssetTransfer.to_service_id == filters.to_service_id)

        if filters.status:
            query = query.where(AssetTransfer.status == filters.status)

        if filters.date_from:
            query = query.where(AssetTransfer.created_at >= filters.date_from)

        if filters.date_to:
            query = query.where(AssetTransfer.created_at <= filters.date_to)

        if filters.search:
            term = f"%{filters.search.strip()}%"
            query = query.join(Asset, isouter=True).where(
                or_(
                    Asset.name.ilike(term),
                    Asset.asset_tag.ilike(term),
                )
            )

        return query

    def _build_filtered_subquery(self, filters: AssetTransferFilterInput):
        return self._apply_filters(
            select(AssetTransfer.id).select_from(AssetTransfer),
            filters,
        ).subquery()

    async def list_transfers(
        self,
        filters: AssetTransferFilterInput,
        pagination: PaginationParams,
    ) -> tuple[list[AssetTransfer], int]:
        """List transfers with pagination."""
        query = (
            select(AssetTransfer)
            .options(
                selectinload(AssetTransfer.asset),
                selectinload(AssetTransfer.created_by),
                selectinload(AssetTransfer.received_by),
                selectinload(AssetTransfer.from_warehouse),
                selectinload(AssetTransfer.to_warehouse),
                selectinload(AssetTransfer.from_service),
                selectinload(AssetTransfer.to_service),
            )
            .order_by(AssetTransfer.created_at.desc())
        )

        query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(AssetTransfer.id)).select_from(AssetTransfer)
        count_query = self._apply_filters(count_query, filters)
        total = await self.session.scalar(count_query)

        # Get paginated results
        result = await self.session.execute(
            query.limit(pagination.limit).offset(pagination.offset())
        )

        return result.scalars().all(), int(total or 0)

    async def list_pending_transfers(self, pagination: PaginationParams) -> tuple[list[AssetTransfer], int]:
        """List pending transfers."""
        query = (
            select(AssetTransfer)
            .where(AssetTransfer.status == TransferStatus.PENDING)
            .options(
                selectinload(AssetTransfer.asset),
                selectinload(AssetTransfer.created_by),
                selectinload(AssetTransfer.from_warehouse),
                selectinload(AssetTransfer.to_warehouse),
                selectinload(AssetTransfer.from_service),
                selectinload(AssetTransfer.to_service),
            )
            .order_by(AssetTransfer.created_at.asc())
        )

        total = await self.session.scalar(
            select(func.count(AssetTransfer.id)).where(AssetTransfer.status == TransferStatus.PENDING)
        )

        result = await self.session.execute(
            query.limit(pagination.limit).offset(pagination.offset())
        )

        return result.scalars().all(), int(total or 0)

    async def get_transfer_history_for_asset(self, asset_id: UUID) -> list[AssetTransfer]:
        """Get complete transfer history for an asset."""
        result = await self.session.execute(
            select(AssetTransfer)
            .where(AssetTransfer.asset_id == asset_id)
            .options(
                selectinload(AssetTransfer.created_by),
                selectinload(AssetTransfer.received_by),
                selectinload(AssetTransfer.from_warehouse),
                selectinload(AssetTransfer.to_warehouse),
                selectinload(AssetTransfer.from_service),
                selectinload(AssetTransfer.to_service),
            )
            .order_by(AssetTransfer.created_at.asc())
        )
        return result.scalars().all()

    async def get_transfer_aggregates(self, filters: AssetTransferFilterInput) -> dict:
        """Get aggregated transfer metrics."""
        filtered = self._build_filtered_subquery(filters)
        aggregates = (
            await self.session.execute(
                select(
                    func.count(filtered.c.id).label("total_transfers"),
                    func.count(filtered.c.id)
                    .filter(AssetTransfer.status == TransferStatus.COMPLETED)
                    .label("completed_transfers"),
                    func.count(filtered.c.id)
                    .filter(AssetTransfer.status == TransferStatus.PENDING)
                    .label("pending_transfers"),
                    func.count(filtered.c.id)
                    .filter(AssetTransfer.status == TransferStatus.CANCELLED)
                    .label("cancelled_transfers"),
                    func.avg(AssetTransfer.transferred_at - AssetTransfer.created_at)
                    .filter(
                        and_(
                            AssetTransfer.status == TransferStatus.COMPLETED,
                            AssetTransfer.transferred_at.isnot(None),
                        )
                    )
                    .label("average_completion_duration"),
                    func.max(AssetTransfer.transferred_at - AssetTransfer.created_at)
                    .filter(
                        and_(
                            AssetTransfer.status == TransferStatus.COMPLETED,
                            AssetTransfer.transferred_at.isnot(None),
                        )
                    )
                    .label("longest_completion_duration"),
                    func.min(AssetTransfer.transferred_at - AssetTransfer.created_at)
                    .filter(
                        and_(
                            AssetTransfer.status == TransferStatus.COMPLETED,
                            AssetTransfer.transferred_at.isnot(None),
                        )
                    )
                    .label("shortest_completion_duration"),
                )
                .select_from(filtered)
                .join(AssetTransfer, AssetTransfer.id == filtered.c.id)
            )
        ).one()

        # Oldest pending transfer
        oldest_pending = await self.session.execute(
            select(AssetTransfer.id, AssetTransfer.created_at)
            .select_from(filtered)
            .join(AssetTransfer, AssetTransfer.id == filtered.c.id)
            .where(AssetTransfer.status == TransferStatus.PENDING)
            .order_by(AssetTransfer.created_at.asc())
            .limit(1)
        )
        oldest_pending_row = oldest_pending.first()
        oldest_pending_days = None
        oldest_pending_id = None
        if oldest_pending_row:
            oldest_pending_days = (utc_now() - oldest_pending_row[1]).days
            oldest_pending_id = oldest_pending_row[0]

        bottlenecks = (
            await self.session.execute(
                select(
                    func.count(filtered.c.id)
                    .filter(
                        and_(
                            AssetTransfer.status == TransferStatus.PENDING,
                            AssetTransfer.created_at <= utc_now() - timedelta(days=7),
                        )
                    )
                    .label("over_7_days"),
                    func.count(filtered.c.id)
                    .filter(
                        and_(
                            AssetTransfer.status == TransferStatus.PENDING,
                            AssetTransfer.created_at <= utc_now() - timedelta(days=30),
                        )
                    )
                    .label("over_30_days"),
                )
                .select_from(filtered)
                .join(AssetTransfer, AssetTransfer.id == filtered.c.id)
            )
        ).one()

        return {
            "total_transfers": int(aggregates.total_transfers or 0),
            "completed_transfers": int(aggregates.completed_transfers or 0),
            "pending_transfers": int(aggregates.pending_transfers or 0),
            "cancelled_transfers": int(aggregates.cancelled_transfers or 0),
            "average_completion_time_days": Decimal(aggregates.average_completion_duration.total_seconds() / 86400) if aggregates.average_completion_duration else None,
            "longest_completion_time_days": Decimal(aggregates.longest_completion_duration.total_seconds() / 86400) if aggregates.longest_completion_duration else None,
            "shortest_completion_time_days": Decimal(aggregates.shortest_completion_duration.total_seconds() / 86400) if aggregates.shortest_completion_duration else None,
            "oldest_pending_transfer_days": oldest_pending_days,
            "oldest_pending_transfer_id": oldest_pending_id,
            "transfers_pending_over_7_days": int(bottlenecks.over_7_days or 0),
            "transfers_pending_over_30_days": int(bottlenecks.over_30_days or 0),
        }

    async def get_bottlenecks(self, critical_days: int = 30, warning_days: int = 7) -> dict:
        """Get transfer bottlenecks."""
        now = utc_now()

        # Critical: pending > critical_days
        critical_result = await self.session.execute(
            select(AssetTransfer)
            .where(
                and_(
                    AssetTransfer.status == TransferStatus.PENDING,
                    AssetTransfer.created_at <= now - timedelta(days=critical_days)
                )
            )
            .options(
                selectinload(AssetTransfer.asset),
                selectinload(AssetTransfer.created_by),
                selectinload(AssetTransfer.from_warehouse),
                selectinload(AssetTransfer.to_warehouse),
                selectinload(AssetTransfer.from_service),
                selectinload(AssetTransfer.to_service),
            )
            .order_by(AssetTransfer.created_at.asc())
        )
        critical = critical_result.scalars().all()

        # Warning: pending > warning_days but <= critical_days
        warning_result = await self.session.execute(
            select(AssetTransfer)
            .where(
                and_(
                    AssetTransfer.status == TransferStatus.PENDING,
                    AssetTransfer.created_at <= now - timedelta(days=warning_days),
                    AssetTransfer.created_at > now - timedelta(days=critical_days)
                )
            )
            .options(
                selectinload(AssetTransfer.asset),
                selectinload(AssetTransfer.created_by),
                selectinload(AssetTransfer.from_warehouse),
                selectinload(AssetTransfer.to_warehouse),
                selectinload(AssetTransfer.from_service),
                selectinload(AssetTransfer.to_service),
            )
            .order_by(AssetTransfer.created_at.asc())
        )
        warning = warning_result.scalars().all()

        return {
            "critical": critical,
            "warning": warning,
        }

    async def get_warehouse_transfer_metrics(self, warehouse_id: UUID) -> dict:
        """Get transfer metrics for a specific warehouse."""
        # Transfers FROM warehouse
        from_count = await self.session.scalar(
            select(func.count(AssetTransfer.id)).where(
                AssetTransfer.from_warehouse_id == warehouse_id
            )
        )

        # Transfers TO warehouse
        to_count = await self.session.scalar(
            select(func.count(AssetTransfer.id)).where(
                AssetTransfer.to_warehouse_id == warehouse_id
            )
        )

        # Pending IN
        pending_in = await self.session.scalar(
            select(func.count(AssetTransfer.id)).where(
                and_(
                    AssetTransfer.to_warehouse_id == warehouse_id,
                    AssetTransfer.status == TransferStatus.PENDING
                )
            )
        )

        # Pending OUT
        pending_out = await self.session.scalar(
            select(func.count(AssetTransfer.id)).where(
                and_(
                    AssetTransfer.from_warehouse_id == warehouse_id,
                    AssetTransfer.status == TransferStatus.PENDING
                )
            )
        )

        # Average duration for completed
        avg_dur_result = await self.session.execute(
            select(
                func.avg(AssetTransfer.transferred_at - AssetTransfer.created_at).label("avg_duration")
            ).where(
                and_(
                    or_(
                        AssetTransfer.from_warehouse_id == warehouse_id,
                        AssetTransfer.to_warehouse_id == warehouse_id
                    ),
                    AssetTransfer.status == TransferStatus.COMPLETED,
                    AssetTransfer.transferred_at.isnot(None)
                )
            )
        )

        avg_dur = avg_dur_result.scalar()

        # Get warehouse info
        warehouse = await self.session.get(Warehouse, warehouse_id)

        return {
            "warehouse_id": warehouse_id,
            "warehouse_name": warehouse.name if warehouse else "Unknown",
            "transfers_from": from_count or 0,
            "transfers_to": to_count or 0,
            "pending_in": pending_in or 0,
            "pending_out": pending_out or 0,
            "average_duration_days": Decimal(avg_dur.total_seconds() / 86400) if avg_dur else None,
        }
