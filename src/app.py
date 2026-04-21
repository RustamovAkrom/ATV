from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from api.routers.v1 import router as api_router
from core.config import Settings, get_settings
from core.exceptions.handlers import configure_exception_handlers
from core.lifespan import lifespan
from core.observability.monitoring import router as monitoring_router
from core.slowapi import limiter
from middlewares.audit import AuditMiddleware
from middlewares.logging import LoggingMiddleware
from middlewares.metrics import MetricsMiddleware
from middlewares.request_id import RequestIDMiddleware


def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        root_path=settings.ROOT_PATH,
        docs_url=None if settings.ENV == "prod" else "/docs",
        redoc_url=None if settings.ENV == "prod" else "/redoc",
        openapi_url=None if settings.ENV == "prod" else "/openapi.json",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        generate_unique_id_function=custom_generate_unique_id,
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

    app.add_middleware(RequestIDMiddleware) # request id
    app.add_middleware(LoggingMiddleware) # logging
    app.add_middleware(MetricsMiddleware) # Metrics

    app.add_middleware(AuditMiddleware) # audit
    app.add_middleware(SlowAPIMiddleware) # rate limit (SowAPI)
    app.add_middleware( # session
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        max_age=60 * 60 * 24, # 1 day
        same_site="lax",
        https_only=not settings.DEBUG, # secure in prod
    )
