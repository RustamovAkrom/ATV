from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.middleware.cors import CORSMiddleware
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

from core.admin.registry import setup_admin


def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    path = route.path.replace("/", "_").strip("_")
    return f"{tag}_{path}_{route.name}"

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        root_path=settings.ROOT_PATH,
        docs_url=None,
        redoc_url=None,
        openapi_url=None if settings.ENV == "prod" else "/openapi.json",
        lifespan=lifespan,
        generate_unique_id_function=custom_generate_unique_id,
    )
    # Static files
    configure_staticfiles(app, settings)

    app.state.limiter = limiter

    configure_routes(app, settings)
    configure_middlewares(app, settings)
    configure_exception_handlers(app)

    # Admin Panel
    setup_admin(app, settings)

    return app

def configure_staticfiles(app: FastAPI, settings: Settings):
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="/static/swagger/redoc.standalone.js",
        )


def configure_routes(app: FastAPI, settings: Settings):
    app.include_router(router=monitoring_router, tags=["Monitoring"])
    app.include_router(router=api_router)


def configure_middlewares(app: FastAPI, settings: Settings):
    # Trusted hosts for example: ("localhost", "example.test")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    # CORS Headers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestIDMiddleware)  # request id
    app.add_middleware(LoggingMiddleware)  # logging
    app.add_middleware(MetricsMiddleware)  # Metrics

    app.add_middleware(AuditMiddleware)  # audit
    app.add_middleware(SlowAPIMiddleware)  # rate limit (SowAPI)
    app.add_middleware(  # session
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        max_age=60 * 60 * 24,  # 1 day
        same_site="lax",
        https_only=not settings.DEBUG,  # secure in prod
    )
