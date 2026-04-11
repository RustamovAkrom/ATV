from fastapi import APIRouter, Depends
from core.security.permissions import require_any_role
from core.security.dependencies import get_current_user
from core.security.types import CurrentUser


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/dashboard")
async def dashboard(
    _=Depends(require_any_role(["admin", "manager"])),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, str]:
    return {"message": f"Welcome {current_user}"}
