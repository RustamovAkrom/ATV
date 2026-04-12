from fastapi import APIRouter
from api.v1.auth import router as auth_router
from api.v1.dashboard import router as dashboard_router
from api.v1.audit import router as audit_log_router
from api.v1.security import router as security_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(dashboard_router)
router.include_router(audit_log_router)
router.include_router(security_router)
