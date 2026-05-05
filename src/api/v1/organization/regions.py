"""API endpoints for regions management."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies.organizations.regions import get_region_service
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import RegionPermissions
from schemas.auth.auth import CurrentUserSchema
from services.organization.region_service import RegionService


router = APIRouter(prefix="/regions", tags=["Regions"])


@router.get(
    "/tree",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(RegionPermissions.CanViewRegions)],
)
async def get_regions_tree(
    service: RegionService = Depends(get_region_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Get regions as hierarchical tree structure."""
    return await service.get_tree()


@router.get(
    "/",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(RegionPermissions.CanViewRegions)],
)
async def list_regions(
    service: RegionService = Depends(get_region_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
    level: int | None = Query(None, ge=1, le=4),
    parent_id: UUID | None = None,
):
    """List all regions with optional filtering."""
    return await service.list(level=level, parent_id=parent_id)


@router.get(
    "/{region_id}",
    response_model=dict[str, Any],
    dependencies=[Depends(RegionPermissions.CanViewRegions)],
)
async def get_region(
    region_id: UUID,
    service: RegionService = Depends(get_region_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Get a specific region by ID."""
    region = await service.get(region_id)
    if not region:
        from core.exceptions import NotFoundException

        raise NotFoundException(f"Region {region_id} not found")
    return region
