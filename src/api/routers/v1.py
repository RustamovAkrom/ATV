from fastapi import APIRouter

from api.v1.audit import router as audit_log_router
from api.v1.audit_stream import router as audit_stream_router
from api.v1.auth import router as auth_router
from api.v1.dashboard import router as dashboard_router
from api.v1.rbac import router as rbac_router
from api.v1.security import router as security_router
from api.v1.sessions import router as sessions_router
from api.v1.users import router as users_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(dashboard_router)
router.include_router(security_router)
router.include_router(sessions_router)
router.include_router(rbac_router)
router.include_router(audit_log_router)
router.include_router(audit_stream_router)
