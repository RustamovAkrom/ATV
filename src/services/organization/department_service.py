from __future__ import annotations

from uuid import UUID

from core.exceptions.errors import BadRequest, Conflict, NotFound
from db.models.org.department import Department
from repositories.organization.department_repo import DepartmentRepository
from schemas.organization.department import (
    DepartmentCreateSchema,
    DepartmentDetailSchema,
    DepartmentOutSchema,
    DepartmentRegionRefSchema,
    DepartmentServiceRefSchema,
    DepartmentUpdateSchema,
)
from utils.slug import slugify


class DepartmentService:
    def __init__(self, repo: DepartmentRepository):
        self.repo = repo

    async def list(
        self,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> list[DepartmentOutSchema]:
        departments = await self.repo.list(region_id, service_id, is_active)
        return [self._to_out_schema(department) for department in departments]

    async def get(self, department_id: UUID) -> DepartmentDetailSchema:
        department = await self.repo.get(department_id)
        if department is None:
            raise NotFound(f"Department {department_id} not found")
        return self._to_detail_schema(department)

    async def create(self, data: DepartmentCreateSchema) -> DepartmentDetailSchema:
        await self._validate_references(
            data.region_id,
            data.parent_id,
            data.service_ids,
        )

        if await self.repo.check_name_exists(data.name):
            raise Conflict(f"Department with name '{data.name}' already exists")

        payload = data.model_dump(exclude={"service_ids"})
        payload["slug"] = slugify(data.name)
        payload["meta"] = payload.get("meta") or {}

        department = await self.repo.create(payload)
        try:
            await self.repo.set_services(department.id, data.service_ids)
        except Conflict as exc:
            await self.repo.delete(department.id)
            raise Conflict(str(exc)) from exc
        except Exception as exc:
            await self.repo.delete(department.id)
            raise BadRequest(f"Failed to attach services: {exc!s}") from exc

        return await self.get(department.id)

    async def update(
        self, department_id: UUID, data: DepartmentUpdateSchema
    ) -> DepartmentDetailSchema:
        department = await self.repo.get(department_id)
        if department is None:
            raise NotFound(f"Department {department_id} not found")

        if data.name and await self.repo.check_name_exists(
            data.name, exclude_id=department_id
        ):
            raise Conflict(f"Department with name '{data.name}' already exists")

        next_region_id = (
            data.region_id if data.region_id is not None else department.region_id
        )
        await self._validate_references(
            next_region_id,
            data.parent_id,
            data.service_ids,
        )

        payload = data.model_dump(exclude_unset=True, exclude={"service_ids"})
        if "name" in payload:
            payload["slug"] = slugify(payload["name"])
        if "meta" in payload:
            payload["meta"] = payload["meta"] or {}

        if payload:
            updated = await self.repo.update(department_id, payload)
            if updated is None:
                raise BadRequest(f"Could not update department {department_id}")

        if data.service_ids is not None:
            await self.repo.set_services(department_id, data.service_ids)

        return await self.get(department_id)

    async def delete(self, department_id: UUID) -> None:
        department = await self.repo.get(department_id)
        if department is None:
            raise NotFound(f"Department {department_id} not found")
        await self.repo.delete(department_id)

    async def _validate_references(
        self,
        region_id: UUID | None,
        parent_id: UUID | None,
        service_ids: list[UUID] | None,
    ) -> None:
        if region_id is not None and await self.repo.get_region(region_id) is None:
            raise NotFound(f"Region {region_id} not found")

        if parent_id is not None and await self.repo.get(parent_id) is None:
            raise NotFound(f"Parent department {parent_id} not found")

        for service_id in service_ids or []:
            if await self.repo.get_service(service_id) is None:
                raise NotFound(f"Service {service_id} not found")

    @staticmethod
    def _to_out_schema(department: Department) -> DepartmentOutSchema:
        return DepartmentOutSchema(
            id=department.id,
            name=department.name,
            slug=department.slug,
            description=department.description,
            region_id=department.region_id,
            parent_id=department.parent_id,
            service_ids=[service.id for service in department.services],
            address=department.address,
            latitude=department.latitude,
            longitude=department.longitude,
            contact_phone=department.contact_phone,
            contact_email=department.contact_email,
            is_active=department.is_active,
            meta=department.meta or {},
            created_at=department.created_at,
            updated_at=department.updated_at,
        )

    @classmethod
    def _to_detail_schema(cls, department: Department) -> DepartmentDetailSchema:
        payload = cls._to_out_schema(department).model_dump()
        payload["region"] = DepartmentRegionRefSchema(
            id=department.region.id,
            name=department.region.name,
            latitude=department.region.latitude,
            longitude=department.region.longitude,
        )
        payload["services"] = [
            DepartmentServiceRefSchema(
                id=service.id,
                name=service.name,
                slug=service.slug,
            )
            for service in department.services
        ]
        return DepartmentDetailSchema.model_validate(payload)
