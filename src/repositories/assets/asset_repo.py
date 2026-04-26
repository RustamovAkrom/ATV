from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload, selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.assets.asset_class import AssetClass
from db.models.assets.asset_history import AssetHistory
from db.models.assets.asset_model import AssetModel
from db.models.org.region import Region
from db.models.org.service import Service
from db.models.users.permission import Role
from db.models.users.user import User
from schemas.assets.assets import AssetFilters
from schemas.pagination import PaginationParamsSchema


class AssetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _list_options(self):
        return (
            selectinload(Asset.model),
            selectinload(Asset.asset_class),
            selectinload(Asset.owner),
            selectinload(Asset.region),
            selectinload(Asset.service),
            selectinload(Asset.warehouse),
        )

    def _detail_options(self):
        return self._list_options() + (
            selectinload(Asset.assignments).selectinload(AssetAssignment.user),
            selectinload(Asset.history_entries).selectinload(AssetHistory.user),
        )

    def _base_query(self):
        return select(Asset).options(*self._list_options())

    async def list(self, filters: AssetFilters, pagination: PaginationParamsSchema):
        base = self._apply_filters(select(Asset), filters)

        total = await self.session.scalar(
            select(func.count()).select_from(base.subquery())
        )

        query = (
            base.options(*self._list_options())
            .order_by(Asset.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset())
        )

        result = await self.session.execute(query)
        return result.scalars().unique().all(), int(total or 0)

    async def iter_for_export(self, filters: AssetFilters, chunk_size: int = 100):
        offset = 0
        while True:
            base = self._apply_filters(select(Asset), filters)

            query = (
                base.options(*self._list_options())
                .order_by(Asset.created_at.desc())
                .limit(chunk_size)
                .offset(offset)
            )

            result = await self.session.execute(query)
            items = result.scalars().unique().all()

            if not items:
                break

            for item in items:
                yield item

            offset += chunk_size

    async def count_for_export(self, filters: AssetFilters) -> int:
        base = self._apply_filters(select(Asset), filters)
        total = await self.session.scalar(
            select(func.count()).select_from(base.subquery())
        )
        return int(total or 0)

    def _apply_filters(self, query, filters: AssetFilters):
        if filters.owner_id is not None:
            query = query.where(Asset.owner_id == filters.owner_id)

        if filters.region_id is not None:
            query = query.where(Asset.region_id == filters.region_id)

        if filters.service_id is not None:
            query = query.where(Asset.service_id == filters.service_id)

        if filters.class_id is not None:
            query = query.where(Asset.class_id == filters.class_id)

        if filters.manufacturer_id is not None or filters.category_id is not None:
            query = query.join(Asset.model)

        if filters.manufacturer_id is not None:
            query = query.where(AssetModel.manufacturer_id == filters.manufacturer_id)

        if filters.category_id is not None:
            query = query.where(AssetModel.category_id == filters.category_id)

        if filters.status is not None:
            query = query.where(Asset.status == filters.status)

        if filters.search:
            term = filters.search.strip().lower()[:100]
            like = f"%{term}%"
            query = query.where(
                or_(
                    func.lower(Asset.name).ilike(like),
                    func.lower(Asset.type).ilike(like),
                    func.lower(Asset.asset_tag).ilike(like),
                    func.lower(Asset.serial_number).ilike(like),
                )
            )

        return query

    async def get_by_id(
        self, asset_id: UUID, include_history: bool = True
    ) -> Asset | None:
        query = select(Asset).where(Asset.id == asset_id)

        options = self._detail_options() if include_history else self._list_options()

        result = await self.session.execute(query.options(*options))
        return result.scalar_one_or_none()

    async def get_by_id_for_update(
        self, asset_id: UUID
    ) -> Asset | None:
        result = await self.session.execute(
            select(Asset)
            .options(lazyload("*"))
            .where(Asset.id == asset_id)
            .with_for_update(nowait=True)
        )
        return result.scalar_one_or_none()

    async def get_asset_class(self, class_id: UUID) -> AssetClass | None:
        return await self.session.get(AssetClass, class_id)

    async def get_model(self, model_id: UUID) -> AssetModel | None:
        return await self.session.get(AssetModel, model_id)

    async def get_region(self, region_id: UUID) -> Region | None:
        return await self.session.get(Region, region_id)

    async def get_service(self, service_id: UUID) -> Service | None:
        return await self.session.get(Service, service_id)

    async def get_user(self, user_id: UUID) -> User | None:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.role).selectinload(Role.permissions))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def asset_tag_exists(
        self, asset_tag: str, exclude_id: UUID | None = None
    ) -> bool:
        query = select(Asset.id).where(Asset.asset_tag == asset_tag)

        if exclude_id:
            query = query.where(Asset.id != exclude_id)

        result = await self.session.execute(query.limit(1))
        return result.scalar_one_or_none() is not None

    async def serial_number_exists(
        self, serial_number: str, exclude_id: UUID | None = None
    ) -> bool:
        query = select(Asset.id).where(Asset.serial_number == serial_number)

        if exclude_id:
            query = query.where(Asset.id != exclude_id)

        result = await self.session.execute(query.limit(1))
        return result.scalar_one_or_none() is not None

    async def create(self, asset: Asset) -> Asset:
        self.session.add(asset)
        await self.session.flush()
        return asset

    async def delete(self, asset: Asset) -> None:
        await self.session.delete(asset)
        await self.session.flush()

    async def flush(self) -> None:
        await self.session.flush()

    async def get_active_assignment(self, asset_id: UUID) -> AssetAssignment | None:
        result = await self.session.execute(
            select(AssetAssignment)
            .where(
                AssetAssignment.asset_id == asset_id,
                AssetAssignment.unassigned_at.is_(None),
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def close_active_assignment(
        self, assignment: AssetAssignment, timestamp: datetime
    ) -> None:
        assignment.unassigned_at = timestamp
        await self.session.flush()

    async def add_assignment(self, assignment: AssetAssignment) -> AssetAssignment:
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def add_history(self, history_entry: AssetHistory) -> AssetHistory:
        self.session.add(history_entry)
        await self.session.flush()
        return history_entry
