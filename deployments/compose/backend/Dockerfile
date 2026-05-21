# syntax=docker/dockerfile:1.2
ARG PYTHON_VERSION=3.11
ARG UV_VERSION=0.7.2

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM python:${PYTHON_VERSION} AS builder
COPY --from=uv /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_PYTHON_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_HTTP_TIMEOUT=300

WORKDIR /app

# copy dependenci specifications
COPY ./pyproject.toml ./uv.lock ./


# create and install requirements in /opt/venv (without movements)
RUN uv sync --frozen --no-dev

FROM python:${PYTHON_VERSION} AS app

WORKDIR /app

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=${PYTHONPATH}:/app \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"


# Copy and set permissions for celery worker start script
COPY ./deployments/compose/backend/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker && chmod +x /start-celeryworker

# Copy and set permissions for celery beat start script
COPY ./deployments/compose/backend/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat && chmod +x /start-celerybeat

# Copy and set permissions for flower start script
COPY ./deployments/compose/backend/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower && chmod +x /start-flower

# Copy and set permissions for entrypoint script
COPY ./deployments/compose/backend/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint

# Copy and set permissions for start script
COPY ./deployments/compose/backend/start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start

# Копируем готовое окружение
COPY --from=builder /opt/venv /opt/venv
COPY src /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /opt/venv

USER appuser

ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
