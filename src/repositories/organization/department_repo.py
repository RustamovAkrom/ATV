from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions.errors import Conflict
from db.models.org.department import Department, department_services
from db.models.org.region import Region
from db.models.org.service import Service
from repositories.base import BaseRepository


class DepartmentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> list[Department]:
        query = (
            select(Department)
            .options(selectinload(Department.services))
            .order_by(Department.name)
        )
        if region_id is not None:
            query = query.where(Department.region_id == region_id)
        if is_active is not None:
            query = query.where(Department.is_active == is_active)
        if service_id is not None:
            query = query.join(department_services).where(
                department_services.c.service_id == service_id
            )

        result = await self.session.execute(query)
        return list(result.scalars().unique().all())

    async def get(self, department_id: UUID) -> Department | None:
        result = await self.session.execute(
            select(Department)
            .options(selectinload(Department.services))
            .where(Department.id == department_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Department:
        department = Department(**data)
        self.add(department)
        await self.flush()
        await self.refresh(department)
        return department

    async def update(self, department_id: UUID, data: dict) -> Department | None:
        await self.session.execute(
            update(Department).where(Department.id == department_id).values(**data)
        )
        await self.flush()
        return await self.get(department_id)

    async def delete(self, department_id: UUID) -> bool:
        await self.session.execute(
            delete(department_services).where(
                department_services.c.department_id == department_id
            )
        )
        result = await self.session.execute(
            delete(Department).where(Department.id == department_id)
        )
        await self.flush()
        return self._rowcount(result) > 0

    async def check_name_exists(
        self, name: str, exclude_id: UUID | None = None
    ) -> bool:
        query = select(Department).where(Department.name == name)
        if exclude_id is not None:
            query = query.where(Department.id != exclude_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_region(self, region_id: UUID) -> Region | None:
        return await self.session.get(Region, region_id)

    async def get_service(self, service_id: UUID) -> Service | None:
        return await self.session.get(Service, service_id)

    async def set_services(self, department_id: UUID, service_ids: list[UUID]) -> None:
        await self.session.execute(
            delete(department_services).where(
                department_services.c.department_id == department_id
            )
        )

        for service_id in service_ids:
            service = await self.get_service(service_id)
            if service is None:
                raise Conflict(f"Service with id '{service_id}' not found")

            await self.session.execute(
                department_services.insert().values(
                    department_id=department_id,
                    service_id=service_id,
                )
            )

        await self.flush()
