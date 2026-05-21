# ATV Platform — Общая инфраструктура проекта

## 📌 Что это за проект?

ATV (Axborot-Texnika Vositalari) — это backend-платформа для государственных организаций, предназначенная для централизованного управления техническими средствами, мониторинга и аналитики.

**Основные решаемые проблемы:**
- Единый реестр технических средств
- Управление распределением по регионам и службам
- Контроль складов и запчастей
- Отслеживание ремонтных процессов
- Расчёт расходов
- Аналитика и прогнозирование

---

## 🏗 Архитектура проекта

Проект построен по принципам **Modular Clean Architecture**:

```
Request → Middleware → API Router → Dependency → Service → Repository → Database
                                    ↓
                              Domain Events
                              (History + Audit + Notifications)
```

### Слои приложения

| Слой | Назначение | Расположение |
|------|-----------|-------------|
| **API Layer** | FastAPI роутеры, валидация запросов | `src/api/` |
| **Service Layer** | Бизнес-логика | `src/services/` |
| **Repository Layer** | Доступ к данным, SQL-запросы | `src/repositories/` |
| **Domain Models** | SQLAlchemy модели | `src/db/models/` |
| **Schemas** | Pydantic схемы валидации | `src/schemas/` |
| **Core** | Конфигурация, безопасность, события | `src/core/` |
| **Middlewares** | Audit, логирование, метрики, request-id | `src/middlewares/` |

---

## 🔐 Система безопасности

### Аутентификация
- **JWT** (access + refresh токены)
- Access token — 15 минут (по умолчанию)
- Refresh token — 7 дней
- Refresh token rotation (каждый refresh создаёт новую пару)
- Device binding и IP binding для refresh токенов
- Token blacklist (Redis в production, in-memory в dev)
- Поддержка cookie-based и header-based аутентификации

### Авторизация (RBAC + CAC)
- **RBAC**: Роли → Разрешения (role-based access control)
  - `superadmin` → полный доступ
  - `admin` → CRUD в своём регионе
  - `moderator` → ограниченные операции
  - `analyst` → только чтение аналитики
- **CAC** (Context-based Access Control):
  - Region-scoped доступ (пользователь видит только свой регион)
  - Service-scoped доступ
  - Creator-based доступ (только создатель может удалить/изменить)
  - Multi-level approval checks

### Пароли
- Хеширование: bcrypt (12 rounds)
- Нормализация через SHA-256 (обход 72-байтового лимита bcrypt)

---

## 🔄 Основные потоки данных

### Asset Lifecycle
```
User → создаёт Asset → назначает регион/склад
     → при необходимости создаётся repair
     → используются parts со склада
     → записываются movements
     → все действия логируются в audit_logs
     → рассчитываются расходы
     → генерируется аналитика и прогнозы
```

### Request → Approval → Document Flow
```
Request (заявка) → Approval (многошаговое согласование)
                 → Document (акт/документ)
                 → Commission (комиссия)
                 → Assignment/Transfer (назначение/перемещение)
```

---

## 📊 Модули проекта

| Модуль | Описание | Ключевые эндпоинты |
|--------|----------|-------------------|
| **Auth & Users** | Аутентификация, сессии, RBAC | `/auth/*`, `/users/*`, `/rbac/*` |
| **Organization** | Регионы и службы | `/regions/*`, `/services/*` |
| **Assets** | Технические средства (CRUD, статусы, трансферы) | `/assets/*` |
| **Warehouse** | Склады, запчасти, движения | `/warehouses/*` |
| **Repairs** | Ремонты и ремонтные запчасти | `/assets/repairs/*` |
| **Expenses** | Расходы | `/expenses/*` |
| **Approvals** | Заявки и согласования | `/approvals/*` |
| **Documents** | Документы и файлы | `/assets/documents/*` |
| **Analytics** | Аналитика, прогнозы, алерты | `/analytics/*` |
| **Audit** | Аудит действий и стриминг | `/audit/*` |

---

## 🛠 Технический стек

| Компонент | Технология |
|-----------|-----------|
| **Backend Framework** | FastAPI (Python 3.12+) |
| **База данных** | PostgreSQL |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Миграции** | Alembic |
| **Кэш / Очередь** | Redis |
| **Background Jobs** | Celery |
| **Мониторинг** | Prometheus, Sentry |
| **Rate Limiting** | SlowAPI |
| **Админ-панель** | SQLAdmin |
| **Контейнеризация** | Docker, docker-compose |

---

## 📁 Структура проекта

```
src/
├── api/                    # FastAPI роутеры и зависимости
│   ├── routers/v1.py       # Главный роутер v1
│   ├── v1/                 # Роутеры по модулям
│   │   ├── auth/           # /auth/*
│   │   ├── users/          # /users/*
│   │   ├── assets/         # /assets/*
│   │   ├── analytics/      # /analytics/*
│   │   ├── audit/          # /audit/*
│   │   └── ...
│   └── dependencies/       # FastAPI Depends
├── core/                   # Ядро приложения
│   ├── config.py           # Настройки (Settings)
│   ├── security/           # JWT, пароли, RBAC, blacklist
│   ├── database/           # Async/sync engine, session
│   ├── exceptions/         # Обработчики ошибок
│   ├── events/             # Domain events
│   ├── audit/              # Audit stream (memory/redis)
│   ├── cache/              # Кэширование
│   ├── storage/            # Файловое хранилище
│   ├── notifications/      # Уведомления (DB, WebSocket)
│   ├── observability/      # Prometheus, Sentry
│   ├── admin/              # SQLAdmin конфигурация
│   └── lifespan.py         # Startup/shutdown
├── db/                     # База данных
│   ├── models/             # SQLAlchemy модели
│   ├── migrations/         # Alembic миграции
│   ├── base.py             # Base класс
│   ├── mixins.py           # Примеси (UUID, Timestamp, etc.)
│   └── meta.py             # Метаданные
├── services/               # Бизнес-логика
├── repositories/           # Доступ к данным
├── schemas/                # Pydantic схемы
├── middlewares/            # ASGI middleware
│   ├── audit.py            # Аудит запросов
│   ├── logging.py          # Логирование
│   ├── metrics.py          # Prometheus метрики
│   └── request_id.py       # X-Request-ID
├── tasks/                  # Celery задачи
├── scripts/                # CLI скрипты (bootstrap, cleanup)
├── utils/                  # Вспомогательные утилиты
├── storage/                # Файловое хранилище (локальное)
├── static/                 # Статические файлы (swagger, аватары)
└── templates/              # Jinja2 шаблоны (SQLAdmin)
```

---

## 🚀 Запуск проекта

### Предварительные требования
- Python 3.12+
- PostgreSQL
- Redis (опционально для dev)
- Docker (опционально)

### Быстрый старт

```bash
# 1. Клонирование
git clone <repo-url>
cd atv

# 2. Настройка окружения
cp .env-example .env
# Отредактируйте .env под ваше окружение

# 3. Установка зависимостей
uv sync

# 4. Применение миграций
uv run alembic -c src/alembic.ini upgrade head

# 5. Bootstrap (сидирование RBAC)
uv run python -m scripts.cli bootstrap-rbac

# 6. Создание суперадмина
uv run python -m scripts.cli create-superadmin

# 7. Запуск сервера
uv run src/main.py
```

### Запуск через Docker
```bash
docker-compose up --build
```

### API Документация
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📈 Middleware Pipeline

Порядок выполнения middleware (важен!):

1. **TrustedHostMiddleware** — проверка ALLOWED_HOSTS
2. **CORSMiddleware** — CORS заголовки
3. **RequestIDMiddleware** — X-Request-ID для трассировки
4. **LoggingMiddleware** — логирование запросов
5. **AuditMiddleware** — аудит всех HTTP запросов
6. **SlowAPIMiddleware** — rate limiting
7. **MetricsMiddleware** — Prometheus метрики (последний)
8. **SessionMiddleware** — сессии для SQLAdmin

---

## 📊 Система событий (Domain Events)

Трёхфазный pipeline для побочных эффектов:

```
1. HISTORY (критичный) — запись в историю изменений
2. AUDIT (некритичный) — публикация в audit stream
3. NOTIFICATION (некритичный) — отправка уведомлений
```

Сбои в аудите и уведомлениях **не ломают** бизнес-операцию.

---

## 🔧 Конфигурация

Все настройки через переменные окружения (`.env`). Основные категории:

- `APP_*` — настройки приложения
- `POSTGRES_*` — подключение к БД
- `JWT_*` — настройки токенов
- `REDIS_*` — Redis
- `CELERY_*` — Celery
- `SMTP_*` — Email
- `RATE_LIMIT_*` — Rate limiting
- `STORAGE_*` — Файловое хранилище
- `ALERT_*` — Пороговые значения для алертов
- `LOG_*` — Логирование
- `PROMETHEUS_*` / `SENTRY_*` — Мониторинг

---

## 🧪 Тестирование

```bash
# Запуск всех тестов
uv run pytest

# С coverage
uv run pytest --cov

# Только конкретный файл
uv run pytest tests/test_auth.py
```

---

## 📚 Документация

| Файл | Описание |
|------|----------|
| `README.md` | Общее описание проекта |
| `docs/PROJECT_OVERVIEW.md` | **← этот файл** — общая инфраструктура |
| `docs/TASKS.MD` | План разработки и milestones |
| `docs/ATV_PLATFORMASI_DATABASE_DOKLADI.MD` | Документация БД |
| `docs/API_SPEC/*.md` | Спецификации API по модулям |
| `docs/ASSET_MODELS_PREVIEW.MD` | Превью SQLAlchemy моделей |
| `database.sql` | SQL-схема базы данных |
