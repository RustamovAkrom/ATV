from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.templating import Jinja2Templates

from api.routers.v1 import router as api_router
from core.admin.registry import setup_admin
from core.config import Settings, get_settings
from core.exceptions.handlers import configure_exception_handlers
from core.lifespan import lifespan
from core.observability.monitoring import router as monitoring_router
from core.slowapi import limiter
from middlewares.audit import AuditMiddleware
from middlewares.logging import LoggingMiddleware
from middlewares.metrics import MetricsMiddleware
from middlewares.request_id import RequestIDMiddleware


# ROUTE ID
def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    path = route.path.replace("/", "_").strip("_")
    return f"{tag}_{path}_{route.name}"


# APP FACTORY
def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        root_path=settings.ROOT_PATH,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
        generate_unique_id_function=custom_generate_unique_id,
    )
    app.state.limiter = limiter

    # Настройка шаблонов для админ-панели
    configure_templates(app, settings)
    configure_static(app, settings)
    configure_docs(app, settings)
    configure_routes(app, settings)
    configure_middlewares(app, settings)
    configure_exception_handlers(app)
    setup_admin(app, settings)

    return app


# TEMPLATES (для админ-панели)
def configure_templates(app: FastAPI, settings: Settings):
    """Настройка Jinja2 шаблонов для админ-панели."""
    templates_dir = settings.BASE_DIR / "templates"

    # Создаём директорию если её нет
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)

    # Подключаем шаблоны
    app.templates = Jinja2Templates(directory=str(templates_dir))

    # Делаем шаблоны доступными через app.state
    app.state.templates = app.templates


# STATIC
def configure_static(app: FastAPI, settings: Settings):
    static_dir = settings.BASE_DIR / "static"

    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Также монтируем статику SQLAdmin если есть
    storage_dir = settings.BASE_DIR / settings.STORAGE_ROOT_DIR
    if storage_dir.exists():
        app.mount("/storage", StaticFiles(directory=storage_dir), name="storage")


# DOCS
def configure_docs(app: FastAPI, settings: Settings):
    if not settings.DEBUG:
        return  # PROD: docs disabled

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="/static/swagger/redoc.standalone.js",
        )


def configure_routes(app: FastAPI, settings: Settings):
    """Configure routes."""
    app.include_router(router=monitoring_router, tags=["Monitoring"])
    app.include_router(router=api_router, prefix="/api/v1")


def configure_middlewares(app: FastAPI, settings: Settings):
    # Security first
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Core infra
    app.add_middleware(RequestIDMiddleware)  # request id
    app.add_middleware(LoggingMiddleware)  # logging

    # Business
    app.add_middleware(AuditMiddleware)  # audit

    # Limits
    app.add_middleware(SlowAPIMiddleware)  # rate limit (SowAPI)

    # Observability (LAST)
    # app.add_middleware(MetricsMiddleware)  # Metrics

    # Session (для админ-панели)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        max_age=60 * 60 * 24,  # 1 day
        same_site="lax",
        https_only=not settings.DEBUG,  # secure in prod
    )
