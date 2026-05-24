from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.org.region import Region
from db.models.org.service import Service, region_services
from repositories.base import BaseRepository
from core.exceptions.errors import Conflict


class ServiceRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self) -> list[Service]:
        """Получить список всех сервисов"""
        result = await self.session.execute(
            select(Service).order_by(Service.name)
        )
        return result.scalars().all()

    async def get(self, service_id: UUID) -> Service | None:
        """Получить сервис по ID с загрузкой регионов"""
        result = await self.session.execute(
            select(Service)
            .options(selectinload(Service.regions))
            .where(Service.id == service_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Service:
        """Создать новый сервис"""
        service = Service(**data)
        self.add(service)
        await self.flush()
        await self.refresh(service)
        return service

    async def update(self, service_id: UUID, data: dict) -> Service | None:
        """Обновить сервис"""
        await self.session.execute(
            update(Service)
            .where(Service.id == service_id)
            .values(**data)
        )
        await self.flush()
        return await self.get(service_id)

    async def delete(self, service_id: UUID) -> bool:
        """Удалить сервис (сначала удаляем связи с регионами)"""
        # Сначала удаляем связи с регионами
        await self.session.execute(
            delete(region_services).where(region_services.c.service_id == service_id)
        )
        # Затем удаляем сам сервис
        result = await self.session.execute(
            delete(Service).where(Service.id == service_id)
        )
        await self.flush()
        return result.rowcount > 0

    async def check_name_exists(self, name: str, exclude_id: UUID | None = None) -> bool:
        """Проверить существование сервиса с таким именем"""
        query = select(Service).where(Service.name == name)
        if exclude_id:
            query = query.where(Service.id != exclude_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def check_slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        """Проверить существование сервиса с таким slug"""
        if not slug:
            return False

        query = select(Service).where(Service.slug == slug)
        if exclude_id:
            query = query.where(Service.id != exclude_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def set_regions(self, service_id: UUID, region_ids: list[UUID]) -> None:
        """Привязать регионы к сервису (заменяет все существующие связи)"""
        if not region_ids:
            return

        # Удаляем старые связи
        await self.session.execute(
            delete(region_services).where(region_services.c.service_id == service_id)
        )

        # Добавляем новые связи
        for region_id in region_ids:
            # Проверяем, что регион существует
            region = await self.session.get(Region, region_id)
            if not region:
                raise Conflict(f"Region with id '{region_id}' not found")

            await self.session.execute(
                region_services.insert().values(
                    service_id=service_id,
                    region_id=region_id
                )
            )

        await self.flush()

    async def get_regions(self, service_id: UUID) -> list[Region]:
        """Получить все регионы, привязанные к сервису"""
        result = await self.session.execute(
            select(Region)
            .join(region_services, Region.id == region_services.c.region_id)
            .where(region_services.c.service_id == service_id)
            .order_by(Region.name)
        )
        return result.scalars().all()
