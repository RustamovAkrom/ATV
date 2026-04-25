# repositories/analytics/asset_assignment_analytics_repo.py

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.users.user import User
from schemas.analytics.asset_assignment_analytics import (
    AssetAssignmentFilterInput,
    AssignmentAnalyticsStatus,
)
from schemas.pagination import PaginationParamsSchema


class AssetAssignmentAnalyticsRepository:
    """Read-optimized repository for assignment analytics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _apply_filters(self, query, filters: AssetAssignmentFilterInput):
        """Apply filters to query."""
        filters = filters or AssetAssignmentFilterInput()

        if filters.asset_id:
            query = query.where(AssetAssignment.asset_id == filters.asset_id)

        if filters.user_id:
            query = query.where(AssetAssignment.user_id == filters.user_id)

        if filters.status == AssignmentAnalyticsStatus.ACTIVE:
            query = query.where(AssetAssignment.unassigned_at.is_(None))
        elif filters.status == AssignmentAnalyticsStatus.INACTIVE:
            query = query.where(AssetAssignment.unassigned_at.isnot(None))

        if filters.date_from:
            query = query.where(AssetAssignment.assigned_at >= filters.date_from)

        if filters.date_to:
            query = query.where(AssetAssignment.assigned_at <= filters.date_to)

        if filters.search:
            term = f"%{filters.search.strip()}%"
            query = (
                query.join(Asset)
                .join(User)
                .where(
                    or_(
                        Asset.name.ilike(term),
                        Asset.asset_tag.ilike(term),
                        User.full_name.ilike(term),
                    )
                )
            )

        return query

    def _build_filtered_subquery(self, filters: AssetAssignmentFilterInput):
        return self._apply_filters(
            select(AssetAssignment.id).select_from(AssetAssignment),
            filters,
        ).subquery()

    async def list_assignments(
        self,
        filters: AssetAssignmentFilterInput,
        pagination: PaginationParamsSchema,
    ) -> tuple[list[AssetAssignment], int]:
        """List assignments with pagination."""
        query = (
            select(AssetAssignment)
            .options(
                selectinload(AssetAssignment.asset),
                selectinload(AssetAssignment.user),
            )
            .order_by(AssetAssignment.assigned_at.desc())
        )

        query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(AssetAssignment.id)).select_from(
            AssetAssignment
        )
        count_query = self._apply_filters(count_query, filters)
        total = await self.session.scalar(count_query)

        # Get paginated results
        result = await self.session.execute(
            query.limit(pagination.limit).offset(pagination.offset())
        )

        return result.scalars().all(), int(total or 0)

    async def list_active_assignments(
        self, pagination: PaginationParamsSchema
    ) -> tuple[list[AssetAssignment], int]:
        """List currently active assignments."""
        query = (
            select(AssetAssignment)
            .where(AssetAssignment.unassigned_at.is_(None))
            .options(
                selectinload(AssetAssignment.asset),
                selectinload(AssetAssignment.user),
            )
            .order_by(AssetAssignment.assigned_at.desc())
        )

        total = await self.session.scalar(
            select(func.count(AssetAssignment.id)).where(
                AssetAssignment.unassigned_at.is_(None)
            )
        )

        result = await self.session.execute(
            query.limit(pagination.limit).offset(pagination.offset())
        )

        return result.scalars().all(), int(total or 0)

    async def get_user_assignment_summary(self, user_id: UUID) -> dict:
        """Get summary metrics for a user's assignments."""
        # Active assignments count
        active_count = await self.session.scalar(
            select(func.count(AssetAssignment.id)).where(
                and_(
                    AssetAssignment.user_id == user_id,
                    AssetAssignment.unassigned_at.is_(None),
                )
            )
        )

        # Total assignments count
        total_count = await self.session.scalar(
            select(func.count(AssetAssignment.id)).where(
                AssetAssignment.user_id == user_id
            )
        )

        # Average duration (for completed assignments)
        duration_result = await self.session.execute(
            select(
                func.avg(
                    AssetAssignment.unassigned_at - AssetAssignment.assigned_at
                ).label("avg_duration"),
                func.max(
                    AssetAssignment.unassigned_at - AssetAssignment.assigned_at
                ).label("max_duration"),
            ).where(
                and_(
                    AssetAssignment.user_id == user_id,
                    AssetAssignment.unassigned_at.isnot(None),
                )
            )
        )

        avg_duration, max_duration = duration_result.one()

        # Get user info
        user = await self.session.get(User, user_id)

        return {
            "user_id": user_id,
            "user_name": user.full_name if user else "Unknown",
            "user_email": user.email if user else "",
            "active_assignments_count": active_count or 0,
            "total_assignments_count": total_count or 0,
            "average_duration_days": (
                (avg_duration.total_seconds() / 86400) if avg_duration else None
            ),
            "longest_assignment_days": (
                (max_duration.total_seconds() / 86400) if max_duration else None
            ),
            "recent_assignment_date": await self._get_user_recent_assignment_date(
                user_id
            ),
        }

    async def _get_user_recent_assignment_date(self, user_id: UUID) -> datetime | None:
        """Get most recent assignment date for user."""
        result = await self.session.execute(
            select(func.max(AssetAssignment.assigned_at)).where(
                AssetAssignment.user_id == user_id
            )
        )
        return result.scalar()

    async def get_assignment_timeline(self, asset_id: UUID) -> list[AssetAssignment]:
        """Get complete timeline of assignments for an asset."""
        result = await self.session.execute(
            select(AssetAssignment)
            .where(AssetAssignment.asset_id == asset_id)
            .options(selectinload(AssetAssignment.user))
            .order_by(AssetAssignment.assigned_at.asc())
        )
        return result.scalars().all()

    async def get_aggregates(self, filters: AssetAssignmentFilterInput) -> dict:
        """Get aggregated metrics."""
        filtered = self._build_filtered_subquery(filters)
        aggregates = (
            await self.session.execute(
                select(
                    func.count(filtered.c.id).label("total_assignments"),
                    func.count(filtered.c.id)
                    .filter(AssetAssignment.unassigned_at.is_(None))
                    .label("total_active_assignments"),
                    func.count(filtered.c.id)
                    .filter(AssetAssignment.unassigned_at.isnot(None))
                    .label("total_inactive_assignments"),
                    func.avg(
                        AssetAssignment.unassigned_at - AssetAssignment.assigned_at
                    )
                    .filter(AssetAssignment.unassigned_at.isnot(None))
                    .label("average_assignment_duration"),
                    func.max(
                        AssetAssignment.unassigned_at - AssetAssignment.assigned_at
                    )
                    .filter(AssetAssignment.unassigned_at.isnot(None))
                    .label("longest_assignment_duration"),
                )
                .select_from(filtered)
                .join(AssetAssignment, AssetAssignment.id == filtered.c.id)
            )
        ).one()

        return {
            "total_active_assignments": int(aggregates.total_active_assignments or 0),
            "total_inactive_assignments": int(
                aggregates.total_inactive_assignments or 0
            ),
            "total_assignments": int(aggregates.total_assignments or 0),
            "average_assignment_duration_days": (
                aggregates.average_assignment_duration.total_seconds() / 86400
                if aggregates.average_assignment_duration
                else None
            ),
            "longest_assignment_duration_days": (
                aggregates.longest_assignment_duration.total_seconds() / 86400
                if aggregates.longest_assignment_duration
                else None
            ),
        }

    async def get_most_assigned_asset(self) -> tuple[UUID, str] | None:
        """Get the most frequently assigned asset."""
        result = await self.session.execute(
            select(Asset.id, Asset.name)
            .join(AssetAssignment, Asset.id == AssetAssignment.asset_id)
            .group_by(Asset.id, Asset.name)
            .order_by(func.count(AssetAssignment.id).desc())
            .limit(1)
        )
        row = result.first()
        return (row[0], row[1]) if row else None

    async def get_most_active_user(self) -> tuple[UUID, str] | None:
        """Get the user with most assignments."""
        result = await self.session.execute(
            select(User.id, User.full_name)
            .join(AssetAssignment, User.id == AssetAssignment.user_id)
            .group_by(User.id, User.full_name)
            .order_by(func.count(AssetAssignment.id).desc())
            .limit(1)
        )
        row = result.first()
        return (row[0], row[1]) if row else None
