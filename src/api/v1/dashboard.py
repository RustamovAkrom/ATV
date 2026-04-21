from fastapi import APIRouter, Depends

from core.security.rbac import presets
from core.security.rbac.permissions import Permissions
from schemas.auth_schema import CurrentUserSchema

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/")
async def get_main_dashboard(
    # Используем готовый пресет (пропустит Admin и SuperAdmin)
    user: CurrentUserSchema = presets.IsAdmin,
):
    return {
        "message": f"Welcome {user.id}",
        "role": user.role,
        "permissions": user.permissions
    }


@router.get("/analytics")
async def get_analytics(
    # Используем типизированную проверку через Permissions
    user: CurrentUserSchema = presets.CanViewAudit,
):
    return {
        "message": f"Welcome to analytics dashboard {user.id}",
        "ok": True,
        "role": user.role
    }
