from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions.errors import BadRequest
from db.models.org.department import Department


async def normalize_department_scope(
    session: AsyncSession | None,
    payload: dict[str, Any],
    *,
    department_field: str = "department_id",
    region_field: str = "region_id",
    service_field: str = "service_id",
) -> dict[str, Any]:
    """Validate department scope and normalize region/service values.

    If a department is provided, its region and service values are enforced.
    If the department has exactly one service, that service is filled in.
    """
    department_id = payload.get(department_field)
    if department_id is None:
        return payload

    # If no session provided (e.g. unit tests with fake repos), skip DB lookup
    # and return payload unchanged — higher-level callers can provide a session
    # when DB-backed normalization is required.
    if not session:
        return payload

    department = await session.get(
        Department,
        department_id,
        options=[selectinload(Department.services)],
    )
    if department is None:
        raise BadRequest("Invalid department")

    region_id = payload.get(region_field)
    if region_id is not None and region_id != department.region_id:
        raise BadRequest("Department region does not match provided region")

    payload[region_field] = department.region_id

    service_id = payload.get(service_field)
    if service_id is not None:
        department_service_ids = {service.id for service in department.services}
        if service_id not in department_service_ids:
            raise BadRequest("Department does not include the provided service")
    elif len(department.services) == 1:
        payload[service_field] = department.services[0].id

    return payload
