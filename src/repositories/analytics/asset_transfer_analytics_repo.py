from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_transfer import AssetTransfer
from db.models.enums import TransferStatus
from repositories.analytics.base_analytics_repo import BaseAnalyticsRepository
from schemas.analytics.asset_transfer_analytics import AssetTransferFilterInput
from schemas.pagination import PaginationParamsSchema
from utils.helpers import utc_now


class AssetTransferAnalyticsRepository(BaseAnalyticsRepository):
    """Репозиторий для аналитики трансферов активов"""

    def _apply_filters(self, query, filters: AssetTransferFilterInput):
        """Применяет фильтры к запросу"""
        if not filters:
            return query

        if filters.asset_id:
            query = query.where(AssetTransfer.asset_id == filters.asset_id)
        if filters.created_by_id:
            query = query.where(AssetTransfer.created_by_id == filters.created_by_id)
        if filters.received_by_id:
            query = query.where(AssetTransfer.received_by_id == filters.received_by_id)
        if filters.from_warehouse_id:
            query = query.where(
                AssetTransfer.from_warehouse_id == filters.from_warehouse_id
            )
        if filters.to_warehouse_id:
            query = query.where(
                AssetTransfer.to_warehouse_id == filters.to_warehouse_id
            )
        if filters.from_service_id:
            query = query.where(
                AssetTransfer.from_service_id == filters.from_service_id
            )
        if filters.to_service_id:
            query = query.where(AssetTransfer.to_service_id == filters.to_service_id)
        if filters.status:
            query = query.where(AssetTransfer.status == filters.status)

        date_filters = self.date_filters(
            AssetTransfer.created_at, filters.date_from, filters.date_to
        )
        query = query.where(*date_filters)

        if filters.search:
            term = f"%{filters.search.strip()}%"
            query = query.join(Asset, isouter=True).where(
                or_(
                    Asset.name.ilike(term),
                )
            )

        return query

    async def list_transfers(
        self,
        filters: AssetTransferFilterInput,
        pagination: PaginationParamsSchema,
    ) -> tuple[list[AssetTransfer], int]:
        """Список трансферов с пагинацией"""
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
        result, total = await self.execute_with_pagination(query, pagination)

        return result.scalars().all(), total

    async def list_pending_transfers(
        self, pagination: PaginationParamsSchema
    ) -> tuple[list[AssetTransfer], int]:
        """Список ожидающих трансферов"""
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

        result, total = await self.execute_with_pagination(query, pagination)
        return result.scalars().all(), total

    async def get_transfer_history_for_asset(
        self, asset_id: UUID
    ) -> list[AssetTransfer]:
        """История трансферов для актива"""
        query = (
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

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_bottlenecks(
        self, critical_days: int = 30, warning_days: int = 7
    ) -> dict:
        now = utc_now()

        critical_result = await self.session.execute(
            select(AssetTransfer)
            .where(
                and_(
                    AssetTransfer.status == TransferStatus.PENDING,
                    AssetTransfer.created_at <= now - timedelta(days=critical_days),
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

        warning_result = await self.session.execute(
            select(AssetTransfer)
            .where(
                and_(
                    AssetTransfer.status == TransferStatus.PENDING,
                    AssetTransfer.created_at <= now - timedelta(days=warning_days),
                    AssetTransfer.created_at > now - timedelta(days=critical_days),
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

        return {"critical": critical, "warning": warning}

    async def get_transfer_aggregates(self, filters: AssetTransferFilterInput) -> dict:
        """Агрегированные метрики по трансферам"""
        base_query = select(AssetTransfer.id)
        base_query = self._apply_filters(base_query, filters)
        filtered = base_query.subquery()

        agg_query = (
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
                .label("avg_completion_duration"),
                func.max(AssetTransfer.transferred_at - AssetTransfer.created_at)
                .filter(
                    and_(
                        AssetTransfer.status == TransferStatus.COMPLETED,
                        AssetTransfer.transferred_at.isnot(None),
                    )
                )
                .label("max_completion_duration"),
                func.min(AssetTransfer.transferred_at - AssetTransfer.created_at)
                .filter(
                    and_(
                        AssetTransfer.status == TransferStatus.COMPLETED,
                        AssetTransfer.transferred_at.isnot(None),
                    )
                )
                .label("min_completion_duration"),
            )
            .select_from(filtered)
            .join(AssetTransfer, AssetTransfer.id == filtered.c.id)
        )

        agg_result = (await self.session.execute(agg_query)).one()

        # Старые pending трансферы
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

        # Bottlenecks
        bottlenecks = await self.session.execute(
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
        bottlenecks_row = bottlenecks.one()

        return {
            "total_transfers": int(agg_result.total_transfers or 0),
            "completed_transfers": int(agg_result.completed_transfers or 0),
            "pending_transfers": int(agg_result.pending_transfers or 0),
            "cancelled_transfers": int(agg_result.cancelled_transfers or 0),
            "average_completion_time_days": self._interval_to_days(
                agg_result.avg_completion_duration
            ),
            "longest_completion_time_days": self._interval_to_days(
                agg_result.max_completion_duration
            ),
            "shortest_completion_time_days": self._interval_to_days(
                agg_result.min_completion_duration
            ),
            "oldest_pending_transfer_days": oldest_pending_days,
            "oldest_pending_transfer_id": oldest_pending_id,
            "transfers_pending_over_7_days": int(bottlenecks_row.over_7_days or 0),
            "transfers_pending_over_30_days": int(bottlenecks_row.over_30_days or 0),
        }

    @staticmethod
    def _interval_to_days(interval) -> Decimal | None:
        """Конвертирует interval в дни"""
        if interval is None:
            return None
        return Decimal(interval.total_seconds() / 86400)
