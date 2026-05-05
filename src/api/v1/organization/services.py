"""API endpoints for services management."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.organizations.services import get_service_service
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import ServicePermissions
from schemas.auth.auth import CurrentUserSchema
from services.organization.service_service import ServiceService

router = APIRouter(prefix="/services", tags=["Services"])


@router.get(
    "/",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(ServicePermissions.CanViewServices)],
)
async def list_services(
    service: ServiceService = Depends(get_service_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """List all services."""
    return await service.list()


@router.get(
    "/{service_id}",
    response_model=dict[str, Any],
    dependencies=[Depends(ServicePermissions.CanViewServices)],
)
async def get_service(
    service_id: UUID,
    service: ServiceService = Depends(get_service_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Get a specific service by ID."""
    result = await service.get(service_id)
    if not result:
        from core.exceptions import NotFoundException

        raise NotFoundException(f"Service {service_id} not found")
    return result


@router.get(
    "/{service_id}/regions",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(ServicePermissions.CanViewServices)],
)
async def get_service_regions(
    service_id: UUID,
    service: ServiceService = Depends(get_service_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Get all regions for a specific service."""
    return await service.get_regions(service_id)
