from collections.abc import Callable
from typing import Any

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
from middlewares.request_id import RequestIDMiddleware

# TYPE ALIASES
RouteIDFunction = Callable[[APIRoute], str]


# ROUTE ID GENERATOR
def __custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique operation ID for OpenAPI."""
    tag = route.tags[0] if route.tags else "default"
    path = route.path.replace("/", "_").strip("_")
    return f"{tag}_{path}_{route.name}"


# APP FACTORY
def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings: Settings = get_settings()

    app: FastAPI = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        root_path=settings.ROOT_PATH,
        openapi_url="/api/v1/openapi.json" if settings.DEBUG else None,
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
        generate_unique_id_function=__custom_generate_unique_id,
    )

    app.state.limiter = limiter

    # Configure components
    configure_templates(app, settings)
    configure_static(app, settings)
    configure_docs(app, settings)
    configure_routes(app, settings)
    configure_middlewares(app, settings)
    configure_exception_handlers(app)
    setup_admin(app, settings)

    return app


# TEMPLATES CONFIGURATION
def configure_templates(app: FastAPI, settings: Settings) -> None:
    """Configure Jinja2 templates."""
    templates_dir = settings.BASE_DIR / "templates"

    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)

    app.state.templates = Jinja2Templates(directory=str(templates_dir))


# STATIC FILES CONFIGURATION
def configure_static(app: FastAPI, settings: Settings) -> None:
    """Configure static files serving."""
    static_dir = settings.BASE_DIR / settings.STATIC_ROOT_DIR
    if static_dir.exists():
        app.mount(
            settings.STATIC_URL,
            StaticFiles(directory=static_dir),
            name=settings.STATIC_ROOT_DIR,
        )

    storage_dir = settings.BASE_DIR / settings.STORAGE_ROOT_DIR
    if storage_dir.exists():
        app.mount(
            settings.STORAGE_URL,
            StaticFiles(directory=storage_dir),
            name=settings.STORAGE_ROOT_DIR,
        )


# DOCS CONFIGURATION
def configure_docs(app: FastAPI, settings: Settings) -> None:
    """Configure Swagger and ReDoc UI (development only)."""
    if not settings.DEBUG:
        return

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html() -> Any:
        """Serve Swagger UI."""
        openapi_url: str = app.openapi_url or "/api/v1/openapi.json"
        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=f"{app.title} - Swagger",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger/swagger-ui.css",
        )

    @app.get(str(app.swagger_ui_oauth2_redirect_url), include_in_schema=False)
    async def swagger_ui_redirect() -> Any:
        """Handle OAuth2 redirect for Swagger UI."""
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html() -> Any:
        """Serve ReDoc UI."""
        openapi_url: str = app.openapi_url or "/api/v1/openapi.json"
        return get_redoc_html(
            openapi_url=openapi_url,
            title=f"{app.title} - ReDoc",
            redoc_js_url="/static/swagger/redoc.standalone.js",
        )


# ROUTES CONFIGURATION
def configure_routes(app: FastAPI, settings: Settings) -> None:
    """Configure application routes."""
    app.include_router(router=monitoring_router, tags=["Monitoring"])
    app.include_router(router=api_router, prefix="/api/v1")


# MIDDLEWARES CONFIGURATION
def configure_middlewares(app: FastAPI, settings: Settings) -> None:
    """Configure middleware stack (order matters)."""
    allowed_hosts = list(settings.ALLOWED_HOSTS)
    if settings.ENV != "prod":
        allowed_hosts.extend(["test", "testserver"])

    # Security middleware (first)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Core infrastructure
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)

    # Business middleware
    app.add_middleware(AuditMiddleware)

    # Rate limiting
    app.add_middleware(SlowAPIMiddleware)

    # Session middleware (for admin panel)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        max_age=60 * 60 * 24,  # 1 day
        same_site="lax",
        https_only=not settings.DEBUG,
    )
