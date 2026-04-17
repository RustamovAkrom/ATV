from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from api.router import router as api_router
from core.config import get_settings, Settings
from core.exceptions.handlers import configure_exception_handlers
from core.lifespan import lifespan
from core.observability.monitoring import router as monitoring_router
from core.slowapi import limiter

from middlewares.audit import AuditMiddleware
from middlewares.request_id import RequestIDMiddleware
from middlewares.metrics import MetricsMiddleware



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

    configure_routes(app, settings)
    configure_middlewares(app, settings)
    configure_exception_handlers(app)

    return app

def configure_routes(app: FastAPI, settings: Settings):
    app.include_router(router=monitoring_router, tags=["Monitoring"])
    app.include_router(router=api_router)


def configure_middlewares(app: FastAPI, settings: Settings):
    # Trusted hosts for example: ("localhost", "example.test")
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

    # CORS Headers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(MetricsMiddleware)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(RequestIDMiddleware)

    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        max_age=60 * 60 * 24, # 1 day
        same_site="lax",
        https_only=not settings.DEBUG, # secure in prod
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000) # gzip responses larger than 1KB
