from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from api.router import router as api_router
from core.config import get_settings
from core.exceptions.handlers import register_exception_handlers
from core.lifespan import lifespan
from core.observability.monitoring import router as monitoring_router
from core.slowapi import limiter, rate_limit_exceeded_handler
from middlewares.audit import AuditMiddleware


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        root_path=settings.ROOT_PATH,
        lifespan=lifespan,
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    app.include_router(router=monitoring_router, tags=["Monitoring"])
    app.include_router(router=api_router)
    app.add_middleware(AuditMiddleware)
    register_exception_handlers(app)

    return app
