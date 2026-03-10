-- ===============================================================
-- GOVERNMENT ASSET MANAGEMENT PLATFORM
-- FULL DATABASE STRUCTURE
--
-- Эта схема предназначена для:
-- • системы учета техники (ATV)
-- • мониторинга состояния
-- • аналитики
-- • планирования закупок
-- • аудита
--
-- Подходит для:
-- FastAPI + SQLAlchemy + PostgreSQL
-- ===============================================================



-- ===============================================================
-- CATEGORY: ENUM / REFERENCE TABLES
-- Справочники значений для статусов и типов
-- Используются как "choices" в backend
-- ===============================================================

-- Состояния пользователя
-- active  → активный пользователь
-- disabled → отключен администратором
-- locked → временно заблокирован
CREATE TABLE user_statuses (
    code VARCHAR(50) PRIMARY KEY,
    description TEXT
);


-- Состояния техники
-- active → используется
-- broken → сломано
-- reserve → резерв
-- decommissioned → списано
CREATE TABLE asset_statuses (
    code VARCHAR(50) PRIMARY KEY,
    description TEXT
);


-- Этап жизненного цикла техники
CREATE TABLE lifecycle_stages (
    code VARCHAR(50) PRIMARY KEY,
    description TEXT
);


-- Статус ремонта
CREATE TABLE repair_statuses (
    code VARCHAR(50) PRIMARY KEY,
    description TEXT
);


-- Тип расходов
CREATE TABLE expense_types (
    code VARCHAR(50) PRIMARY KEY,
    description TEXT
);


-- Тип событий техники
CREATE TABLE event_types (
    code VARCHAR(50) PRIMARY KEY,
    description TEXT
);



-- ===============================================================
-- CATEGORY: RBAC / AUTHORIZATION
-- Управление ролями и правами доступа
-- ===============================================================

-- Роли пользователей системы
-- Например:
-- SUPER_ADMIN
-- NATIONAL_ANALYST
-- REGION_OPERATOR
CREATE TABLE roles (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Права доступа (granular permissions)
-- Например:
-- assets.create
-- assets.update
-- analytics.view
CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    code VARCHAR(150) UNIQUE NOT NULL,
    name VARCHAR(255),
    description TEXT
);


-- Связь ролей и прав
-- role → many permissions
CREATE TABLE role_permissions (
    role_id UUID,
    permission_id UUID,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY(role_id, permission_id),

    FOREIGN KEY(role_id) REFERENCES roles(id),
    FOREIGN KEY(permission_id) REFERENCES permissions(id)
);



-- ===============================================================
-- CATEGORY: USERS
-- Основная таблица пользователей системы
-- ===============================================================

-- Пользователи системы
-- identity таблица
CREATE TABLE users (

    -- уникальный идентификатор пользователя
    id UUID PRIMARY KEY,

    -- логин
    username VARCHAR(255) UNIQUE NOT NULL,

    -- email
    email VARCHAR(255) UNIQUE,

    -- телефон
    phone VARCHAR(30) UNIQUE,

    -- ФИО
    full_name VARCHAR(255),

    -- хеш пароля (bcrypt/argon2)
    password_hash VARCHAR(255) NOT NULL,

    -- роль пользователя
    role_id UUID NOT NULL,

    -- статус аккаунта
    status_code VARCHAR(50),

    -- последний вход
    last_login TIMESTAMP,

    -- последняя смена пароля
    last_password_change TIMESTAMP,

    -- количество неудачных попыток входа
    failed_login_attempts INTEGER DEFAULT 0,

    -- включена ли двухфакторная авторизация
    is_two_factor_enabled BOOLEAN DEFAULT FALSE,

    -- дата создания
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- дата изменения
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- optimistic locking
    version INTEGER DEFAULT 1,

    FOREIGN KEY(role_id) REFERENCES roles(id),
    FOREIGN KEY(status_code) REFERENCES user_statuses(code)
);



-- ===============================================================
-- CATEGORY: USER PROFILE
-- Расширенная информация о пользователях
-- ===============================================================

CREATE TABLE user_profiles (

    id UUID PRIMARY KEY,

    -- связь с пользователем
    user_id UUID UNIQUE,

    -- должность
    position VARCHAR(255),

    -- звание
    rank VARCHAR(100),

    -- служебный телефон
    phone_official VARCHAR(30),

    -- ссылка на аватар
    avatar_url TEXT,

    -- описание
    bio TEXT,

    -- регион
    region_id UUID,

    -- подразделение
    department_id UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)
);



-- ===============================================================
-- CATEGORY: USER ACCESS
-- Область доступа пользователей
-- ===============================================================

CREATE TABLE user_scopes (

    id UUID PRIMARY KEY,

    -- пользователь
    user_id UUID NOT NULL,

    -- доступный регион
    region_id UUID,

    -- доступное подразделение
    department_id UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)
);



-- ===============================================================
-- CATEGORY: USER SECURITY
-- Безопасность авторизации
-- ===============================================================

-- устройства пользователя
CREATE TABLE user_devices (

    id UUID PRIMARY KEY,

    user_id UUID,

    -- имя устройства
    device_name VARCHAR(255),

    -- тип устройства
    device_type VARCHAR(50),

    os VARCHAR(100),
    browser VARCHAR(100),

    device_fingerprint VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id)
);


-- активные сессии пользователя
CREATE TABLE user_sessions (

    id UUID PRIMARY KEY,

    user_id UUID NOT NULL,

    device_id UUID,

    -- hash refresh token
    refresh_token_hash VARCHAR(255),

    ip_address VARCHAR(100),

    user_agent TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    expires_at TIMESTAMP,

    revoked_at TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(device_id) REFERENCES user_devices(id)
);



-- ===============================================================
-- CATEGORY: ORGANIZATION STRUCTURE
-- Структура государства
-- ===============================================================

-- регионы
CREATE TABLE regions (

    id UUID PRIMARY KEY,

    name VARCHAR(255) NOT NULL,

    code VARCHAR(50),

    -- уровень
    -- 0 страна
    -- 1 область
    -- 2 район
    level SMALLINT,

    parent_id UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(parent_id) REFERENCES regions(id)
);



-- службы
CREATE TABLE services (

    id UUID PRIMARY KEY,

    name VARCHAR(255),

    code VARCHAR(50) UNIQUE,

    description TEXT
);



-- подразделения
CREATE TABLE departments (

    id UUID PRIMARY KEY,

    name VARCHAR(255),

    region_id UUID NOT NULL,

    service_id UUID,

    manager_user_id UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(region_id) REFERENCES regions(id),
    FOREIGN KEY(service_id) REFERENCES services(id),
    FOREIGN KEY(manager_user_id) REFERENCES users(id)
);



-- ===============================================================
-- CATEGORY: ASSET CATALOG
-- Каталог техники
-- ===============================================================

CREATE TABLE manufacturers (

    id UUID PRIMARY KEY,

    name VARCHAR(255) UNIQUE NOT NULL,

    country VARCHAR(100),

    website VARCHAR(255)
);


CREATE TABLE asset_types (

    id UUID PRIMARY KEY,

    name VARCHAR(255),

    code VARCHAR(50) UNIQUE
);


CREATE TABLE asset_models (

    id UUID PRIMARY KEY,

    type_id UUID,

    manufacturer_id UUID,

    model_name VARCHAR(255),

    lifetime_years INTEGER,

    warranty_months INTEGER,

    FOREIGN KEY(type_id) REFERENCES asset_types(id),
    FOREIGN KEY(manufacturer_id) REFERENCES manufacturers(id)
);



-- ===============================================================
-- CATEGORY: ASSETS
-- Основная таблица техники
-- ===============================================================

CREATE TABLE assets (

    id UUID PRIMARY KEY,

    -- инвентарный номер
    asset_tag VARCHAR(255) UNIQUE,

    model_id UUID NOT NULL,

    -- заводской номер
    serial_number VARCHAR(255) UNIQUE,

    service_id UUID,
    region_id UUID,
    department_id UUID,

    purchase_date DATE,

    purchase_cost DECIMAL(18,2),

    commission_date DATE,

    warranty_end DATE,

    lifetime_years INTEGER,

    status_code VARCHAR(50),

    lifecycle_stage_code VARCHAR(50),

    condition_percent INTEGER,

    created_by UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(model_id) REFERENCES asset_models(id),

    FOREIGN KEY(service_id) REFERENCES services(id),

    FOREIGN KEY(region_id) REFERENCES regions(id),

    FOREIGN KEY(department_id) REFERENCES departments(id),

    FOREIGN KEY(status_code) REFERENCES asset_statuses(code),

    FOREIGN KEY(lifecycle_stage_code) REFERENCES lifecycle_stages(code),

    FOREIGN KEY(created_by) REFERENCES users(id)
);



-- ===============================================================
-- CATEGORY: ASSET HISTORY
-- История перемещений техники
-- ===============================================================

CREATE TABLE asset_assignments (

    id UUID PRIMARY KEY,

    asset_id UUID NOT NULL,

    from_region_id UUID,
    to_region_id UUID,

    from_department_id UUID,
    to_department_id UUID,

    assigned_by UUID,

    assigned_at TIMESTAMP,

    note TEXT,

    FOREIGN KEY(asset_id) REFERENCES assets(id)
);



CREATE TABLE asset_events (

    id UUID PRIMARY KEY,

    asset_id UUID,

    event_type_code VARCHAR(50),

    description TEXT,

    performed_by UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(asset_id) REFERENCES assets(id),

    FOREIGN KEY(event_type_code) REFERENCES event_types(code)
);



-- ===============================================================
-- CATEGORY: MAINTENANCE
-- Ремонты техники
-- ===============================================================

CREATE TABLE repairs (

    id UUID PRIMARY KEY,

    asset_id UUID NOT NULL,

    reported_by UUID,

    reported_at TIMESTAMP,

    repair_date TIMESTAMP,

    description TEXT,

    performed_by VARCHAR(255),

    status_code VARCHAR(50),

    total_cost DECIMAL(18,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(asset_id) REFERENCES assets(id),

    FOREIGN KEY(reported_by) REFERENCES users(id),

    FOREIGN KEY(status_code) REFERENCES repair_statuses(code)
);



CREATE TABLE repair_parts (

    id UUID PRIMARY KEY,

    repair_id UUID NOT NULL,

    name VARCHAR(255),

    part_number VARCHAR(255),

    quantity INTEGER,

    cost DECIMAL(18,2),

    FOREIGN KEY(repair_id) REFERENCES repairs(id)
);



-- ===============================================================
-- CATEGORY: FINANCE
-- Финансовые расходы
-- ===============================================================

CREATE TABLE expenses (

    id UUID PRIMARY KEY,

    asset_id UUID,

    department_id UUID,

    expense_type_code VARCHAR(50),

    amount DECIMAL(18,2),

    currency VARCHAR(10),

    occurred_at TIMESTAMP,

    description TEXT,

    created_by UUID,

    FOREIGN KEY(asset_id) REFERENCES assets(id),

    FOREIGN KEY(department_id) REFERENCES departments(id),

    FOREIGN KEY(expense_type_code) REFERENCES expense_types(code),

    FOREIGN KEY(created_by) REFERENCES users(id)
);



-- ===============================================================
-- CATEGORY: ANALYTICS
-- Прогноз потребности техники
-- ===============================================================

CREATE TABLE forecasts (

    id UUID PRIMARY KEY,

    region_id UUID,

    service_id UUID,

    asset_type_id UUID,

    forecast_year INTEGER,

    demand_estimate INTEGER,

    method VARCHAR(100),

    confidence DECIMAL(5,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- ===============================================================
-- CATEGORY: AUDIT
-- Журнал действий системы
-- ===============================================================

CREATE TABLE audit_logs (

    id UUID PRIMARY KEY,

    actor_user_id UUID,

    action VARCHAR(255),

    object_table VARCHAR(255),

    object_id UUID,

    old_data JSON,

    new_data JSON,

    extra JSON,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- ===============================================================
-- CATEGORY: FILE STORAGE
-- Файлы и документы
-- ===============================================================

CREATE TABLE attachments (

    id UUID PRIMARY KEY,

    object_table VARCHAR(255),

    object_id UUID,

    filename VARCHAR(255),

    url VARCHAR(2048),

    content_type VARCHAR(100),

    created_by UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- ===============================================================
-- CATEGORY: NOTIFICATIONS
-- Система уведомлений
-- ===============================================================

CREATE TABLE notifications (

    id UUID PRIMARY KEY,

    type VARCHAR(50),

    title VARCHAR(255),

    message TEXT,

    entity_type VARCHAR(100),

    entity_id UUID,

    created_by UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE notification_recipients (

    id UUID PRIMARY KEY,

    notification_id UUID,

    user_id UUID,

    is_read BOOLEAN DEFAULT FALSE,

    read_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(notification_id, user_id),

    FOREIGN KEY(notification_id) REFERENCES notifications(id),

    FOREIGN KEY(user_id) REFERENCES users(id)
);