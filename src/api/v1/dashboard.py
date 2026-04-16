from fastapi import APIRouter, Depends, Request

from core.security.rbac.guards import require_roles, require_permissions
from db.models.enums import UserRole
from core.security.auth.types import CurrentUser

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/")
async def dashboard(
    user: CurrentUser = Depends(require_roles(UserRole.ADMIN)),
):
    return {
        "message": f"Welcome {user.id}",
        "role": user.role,
    }


@router.get("/analytics")
async def analytics(
    user: CurrentUser = Depends(require_permissions("assets.read")),
):
    return {
        "message": f"Welcome to analytics dashboard {user.id}",
        "ok": True
    }
