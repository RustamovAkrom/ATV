"""API endpoints for services management."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies.organizations.services import get_service_service
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import ServicePermissions
from core.cache.decorators import cached, invalidate_cache
from core.slowapi import limiter
from schemas.auth.auth import CurrentUserSchema
from schemas.organization.service import (
    ServiceCreateSchema,
    ServiceUpdateSchema,
    ServiceOutSchema,
    ServiceWithRegionsOutSchema,
)
from services.organization.service_service import ServiceService

router = APIRouter(prefix="/services", tags=["Services"])


@router.get(
    "/",
    response_model=list[ServiceOutSchema],
    dependencies=[Depends(ServicePermissions.CanViewServices)],
)
@cached(ttl=30, tags=("service:list",))
async def list_services(
    service: ServiceService = Depends(get_service_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """List all services."""
    return await service.list()


@router.get(
    "/{service_id}",
    response_model=ServiceWithRegionsOutSchema,
    dependencies=[Depends(ServicePermissions.CanViewServices)],
)
@cached(ttl=30, tags=("service:detail",))
async def get_service(
    service_id: UUID,
    service: ServiceService = Depends(get_service_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Get a specific service by ID."""
    return await service.get(service_id)


@router.get(
    "/{service_id}/regions",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(ServicePermissions.CanViewServices)],
)
@cached(ttl=30, tags=("service:regions",))
async def get_service_regions(
    service_id: UUID,
    service: ServiceService = Depends(get_service_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Get all regions for a specific service."""
    return await service.get_regions(service_id)


@router.post(
    "/",
    response_model=ServiceOutSchema,
    dependencies=[Depends(ServicePermissions.CanCreateServices)],
)
@limiter.limit("10/minute")
@invalidate_cache(tags=("service:list", "service:regions",))
async def create_service(
    request: Request,
    data: ServiceCreateSchema,
    service: ServiceService = Depends(get_service_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Create a new service."""
    return await service.create(data)


@router.patch(
    "/{service_id}",
    response_model=ServiceOutSchema,
    dependencies=[Depends(ServicePermissions.CanUpdateServices)],
)
@limiter.limit("20/minute")
@invalidate_cache(tags=("service:list", "service:regions", "service:detail",))
async def update_service(
    request: Request,
    service_id: UUID,
    data: ServiceUpdateSchema,
    service: ServiceService = Depends(get_service_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    return await service.update(service_id, data)


@router.delete(
    "/{service_id}",
    response_model=dict[str, Any],
    dependencies=[Depends(ServicePermissions.CanDeleteServices)],
)
@limiter.limit("5/minute")
@invalidate_cache(tags=("service:list", "service:regions", "service:detail",))
async def delete_service(
    request: Request,
    service_id: UUID,
    service: ServiceService = Depends(get_service_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Delete a service."""
    return await service.delete(service_id)
