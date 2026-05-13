from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.users.user import User
from repositories.analytics.assignment_base_repo import AssignmentBaseRepository
from schemas.analytics.asset_assignment_analytics import AssetAssignmentFilterInput
from schemas.pagination import PaginationParamsSchema


class AssetAssignmentAnalyticsRepository(AssignmentBaseRepository):
    """Repository for asset assignment analytics."""

    async def list_assignments(
        self,
        filters: AssetAssignmentFilterInput,
        pagination: PaginationParamsSchema,
    ) -> tuple[list[AssetAssignment], int]:
        """List assignments with pagination."""
        query = select(AssetAssignment).options(
            selectinload(AssetAssignment.asset),
            selectinload(AssetAssignment.user),
        )

        query = self.apply_assignment_filters(query, filters)
        query = query.order_by(AssetAssignment.assigned_at.desc())

        result, total = await self.execute_with_pagination(query, pagination)
        return result.scalars().all(), total

    async def get_aggregates(self, filters: AssetAssignmentFilterInput) -> dict:
        base_query = select(AssetAssignment.id)
        base_query = self.apply_assignment_filters(base_query, filters, with_joins=False)
        filtered = base_query.subquery()

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
            "total_inactive_assignments": int(aggregates.total_inactive_assignments or 0),
            "total_assignments": int(aggregates.total_assignments or 0),
            "average_assignment_duration_days": (
                aggregates.average_assignment_duration.total_seconds() / 86400
                if aggregates.average_assignment_duration
                else 0.0
            ),
            "longest_assignment_duration_days": (
                aggregates.longest_assignment_duration.total_seconds() / 86400
                if aggregates.longest_assignment_duration
                else 0.0
            ),
        }

    async def get_assignment_timeline(self, asset_id):
        result = await self.session.execute(
            select(AssetAssignment)
            .where(AssetAssignment.asset_id == asset_id)
            .options(
                selectinload(AssetAssignment.asset),
                selectinload(AssetAssignment.user),
            )
            .order_by(AssetAssignment.assigned_at.asc())
        )
        return result.scalars().all()

    async def get_user_assignment_summary(self, user_id):
        aggregate = (
            await self.session.execute(
                select(
                    User.id.label("user_id"),
                    User.full_name.label("user_name"),
                    User.email.label("user_email"),
                    func.count(AssetAssignment.id)
                    .filter(AssetAssignment.unassigned_at.is_(None))
                    .label("active_assignments_count"),
                    func.count(AssetAssignment.id).label("total_assignments_count"),
                    func.avg(AssetAssignment.unassigned_at - AssetAssignment.assigned_at)
                    .filter(AssetAssignment.unassigned_at.isnot(None))
                    .label("average_duration"),
                    func.max(AssetAssignment.unassigned_at - AssetAssignment.assigned_at)
                    .filter(AssetAssignment.unassigned_at.isnot(None))
                    .label("longest_duration"),
                    func.max(AssetAssignment.assigned_at).label("recent_assignment_date"),
                )
                .select_from(User)
                .join(AssetAssignment, AssetAssignment.user_id == User.id, isouter=True)
                .where(User.id == user_id)
                .group_by(User.id, User.full_name, User.email)
            )
        ).one_or_none()

        if not aggregate:
            return {
                "user_id": user_id,
                "user_name": "Unknown",
                "user_email": "",
                "active_assignments_count": 0,
                "total_assignments_count": 0,
                "average_duration_days": None,
                "longest_assignment_days": None,
                "recent_assignment_date": None,
            }

        return {
            "user_id": aggregate.user_id,
            "user_name": aggregate.user_name,
            "user_email": aggregate.user_email or "",
            "active_assignments_count": int(aggregate.active_assignments_count or 0),
            "total_assignments_count": int(aggregate.total_assignments_count or 0),
            "average_duration_days": (
                aggregate.average_duration.total_seconds() / 86400
                if aggregate.average_duration
                else None
            ),
            "longest_assignment_days": (
                aggregate.longest_duration.total_seconds() / 86400
                if aggregate.longest_duration
                else None
            ),
            "recent_assignment_date": aggregate.recent_assignment_date,
        }

    async def get_most_assigned_asset(self):
        row = (
            await self.session.execute(
                select(Asset.id, Asset.name, func.count(AssetAssignment.id).label("cnt"))
                .join(AssetAssignment, AssetAssignment.asset_id == Asset.id)
                .group_by(Asset.id, Asset.name)
                .order_by(func.count(AssetAssignment.id).desc(), Asset.name.asc())
                .limit(1)
            )
        ).first()
        return (row[0], row[1]) if row else None

    async def get_most_active_user(self):
        row = (
            await self.session.execute(
                select(User.id, User.full_name, func.count(AssetAssignment.id).label("cnt"))
                .join(AssetAssignment, AssetAssignment.user_id == User.id)
                .where(AssetAssignment.unassigned_at.is_(None))
                .group_by(User.id, User.full_name)
                .order_by(func.count(AssetAssignment.id).desc(), User.full_name.asc())
                .limit(1)
            )
        ).first()
        return (row[0], row[1]) if row else None
