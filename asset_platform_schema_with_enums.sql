-- =============================================================
-- ATV PLATFORM - FINAL PRODUCTION SQL SCHEMA
-- Izohlar: Uzbek tilida (kısa va tushunarli)
-- PostgreSQL uchun. (pgcrypto kengaytmasi kerak)
-- =============================================================

-- UUID генерацияси учун
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ======================
-- REFERENCE / ENUM TABLES
-- ======================

-- Foydalanuvchi statuslari (active/disabled/locked)
CREATE TABLE IF NOT EXISTS user_statuses (
  code VARCHAR(50) PRIMARY KEY,     -- status kodi
  name VARCHAR(100),                -- qisqa nomi
  description TEXT                  -- batafsil izoh
);

-- Aktiv statuslari (aktiv/nosoz/zaxira/spisok va h.k.)
CREATE TABLE IF NOT EXISTS asset_statuses (
  code VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100),
  description TEXT
);

-- Hayot sikli bosqichlari (new/normal/aging/critical)
CREATE TABLE IF NOT EXISTS lifecycle_stages (
  code VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100),
  description TEXT
);

-- Ta'mirlash statuslari (batafsil)
-- Masalan: reported, diagnostics, approved, in_repair, waiting_parts, completed, rejected
CREATE TABLE IF NOT EXISTS repair_statuses (
  code VARCHAR(50) PRIMARY KEY,     -- masalan 'reported'
  name VARCHAR(100) NOT NULL,       -- ko'rsatiluvchi nom, masalan 'Reported'
  description TEXT,                 -- qo'shimcha izoh
  sort_order INTEGER DEFAULT 100,   -- ro'yxatda tartib uchun
  is_active BOOLEAN DEFAULT true    -- status faolmi
);

-- Xarajat turlari
CREATE TABLE IF NOT EXISTS expense_types (
  code VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100),
  description TEXT
);

-- Aktiv hodisalari turlari (created, transferred, repaired ...)
CREATE TABLE IF NOT EXISTS event_types (
  code VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100),
  description TEXT
);


-- ======================
-- RBAC: ROLES & PERMISSIONS
-- ======================

-- Rollar (SUPER_ADMIN, NATIONAL_ANALYST, REGION_MANAGER va hk.)
CREATE TABLE IF NOT EXISTS roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Granulyar ruxsatlar (assets.create, analytics.view, ...)
CREATE TABLE IF NOT EXISTS permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(150) UNIQUE NOT NULL,
  name VARCHAR(255),
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Role <-> Permission
CREATE TABLE IF NOT EXISTS role_permissions (
  role_id UUID NOT NULL,
  permission_id UUID NOT NULL,
  granted_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY(role_id, permission_id),
  FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE,
  FOREIGN KEY(permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);


-- ======================
-- USERS
-- ======================

-- Asosiy foydalanuvchi identifikatori (auth)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  username VARCHAR(255) UNIQUE NOT NULL,   -- login
  email VARCHAR(255) UNIQUE,               -- email
  phone VARCHAR(30) UNIQUE,                -- tel (ixtiyoriy)

  full_name VARCHAR(255),

  password_hash VARCHAR(255) NOT NULL,     -- parol xeshi

  role_id UUID NOT NULL,                   -- FK -> roles
  status_code VARCHAR(50) NOT NULL,        -- FK -> user_statuses

  last_login TIMESTAMPTZ,
  last_password_change TIMESTAMPTZ,

  failed_login_attempts INTEGER DEFAULT 0,
  is_two_factor_enabled BOOLEAN DEFAULT false,

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  version INTEGER DEFAULT 1,

  FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE RESTRICT,
  FOREIGN KEY(status_code) REFERENCES user_statuses(code) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_users_role ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status_code);


-- ======================
-- USER PROFILE / SCOPE / SECURITY
-- ======================

CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL,            -- 1:1 profile
  position VARCHAR(255),
  rank VARCHAR(100),
  phone_official VARCHAR(30),
  avatar_url TEXT,
  bio TEXT,
  region_id UUID,
  department_id UUID,
  created_at TIMESTAMPTZ DEFAULT now(),

  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY(region_id) REFERENCES regions(id) ON DELETE SET NULL,
  FOREIGN KEY(department_id) REFERENCES departments(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS user_scopes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  region_id UUID,
  department_id UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY(region_id) REFERENCES regions(id) ON DELETE CASCADE,
  FOREIGN KEY(department_id) REFERENCES departments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  device_name VARCHAR(255),
  device_type VARCHAR(50),
  os VARCHAR(100),
  browser VARCHAR(100),
  device_fingerprint VARCHAR(255),
  last_used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  device_id UUID,
  refresh_token_hash VARCHAR(255),
  ip_address VARCHAR(100),
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  expires_at TIMESTAMPTZ,
  revoked_at TIMESTAMPTZ,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY(device_id) REFERENCES user_devices(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_devices_user ON user_devices(user_id);


-- ======================
-- ORGANIZATION: REGIONS / SERVICES / DEPARTMENTS
-- ======================

CREATE TABLE IF NOT EXISTS regions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  code VARCHAR(50),
  level SMALLINT,                -- 0=country,1=region,2=district,3=facility
  parent_id UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(parent_id) REFERENCES regions(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS services (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  code VARCHAR(50) UNIQUE,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS departments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  region_id UUID NOT NULL,
  service_id UUID,
  manager_user_id UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(region_id) REFERENCES regions(id) ON DELETE RESTRICT,
  FOREIGN KEY(service_id) REFERENCES services(id) ON DELETE SET NULL,
  FOREIGN KEY(manager_user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_departments_region ON departments(region_id);


-- ======================
-- ASSET CATALOG: manufacturers, types, models
-- ======================

CREATE TABLE IF NOT EXISTS manufacturers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) UNIQUE NOT NULL,
  country VARCHAR(100),
  website VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS asset_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  code VARCHAR(50) UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS asset_models (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type_id UUID NOT NULL,
  manufacturer_id UUID,
  model_name VARCHAR(255) NOT NULL,
  lifetime_years INTEGER,
  warranty_months INTEGER,
  created_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(type_id) REFERENCES asset_types(id) ON DELETE RESTRICT,
  FOREIGN KEY(manufacturer_id) REFERENCES manufacturers(id) ON DELETE SET NULL
);


-- ======================
-- ASSETS (CORE)
-- ======================

CREATE TABLE IF NOT EXISTS assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_tag VARCHAR(255) UNIQUE,        -- inventar raqami
  model_id UUID NOT NULL,               -- FK -> asset_models
  serial_number VARCHAR(255) UNIQUE,
  service_id UUID,
  region_id UUID,
  department_id UUID,
  purchase_date DATE,
  purchase_cost NUMERIC(18,2),
  commission_date DATE,
  warranty_end DATE,
  lifetime_years INTEGER,
  status_code VARCHAR(50),              -- FK -> asset_statuses
  lifecycle_stage_code VARCHAR(50),     -- FK -> lifecycle_stages
  condition_percent INTEGER CHECK (condition_percent BETWEEN 0 AND 100),
  location JSONB,
  metadata JSONB DEFAULT '{}'::jsonb,
  is_transfer_locked BOOLEAN DEFAULT false,
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  deleted_at TIMESTAMPTZ,
  deleted_by UUID,
  version INTEGER DEFAULT 1,
  FOREIGN KEY(model_id) REFERENCES asset_models(id) ON DELETE RESTRICT,
  FOREIGN KEY(service_id) REFERENCES services(id) ON DELETE SET NULL,
  FOREIGN KEY(region_id) REFERENCES regions(id) ON DELETE SET NULL,
  FOREIGN KEY(department_id) REFERENCES departments(id) ON DELETE SET NULL,
  FOREIGN KEY(status_code) REFERENCES asset_statuses(code) ON DELETE SET NULL,
  FOREIGN KEY(lifecycle_stage_code) REFERENCES lifecycle_stages(code) ON DELETE SET NULL,
  FOREIGN KEY(created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY(updated_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY(deleted_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_assets_region ON assets(region_id);
CREATE INDEX IF NOT EXISTS idx_assets_department ON assets(department_id);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status_code);
CREATE INDEX IF NOT EXISTS idx_assets_model ON assets(model_id);


-- ======================
-- ASSET HISTORY: assignments & events
-- ======================

CREATE TABLE IF NOT EXISTS asset_assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id UUID NOT NULL,
  from_region_id UUID,
  to_region_id UUID,
  from_department_id UUID,
  to_department_id UUID,
  assigned_by UUID,
  assigned_at TIMESTAMPTZ DEFAULT now(),
  note TEXT,
  FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE,
  FOREIGN KEY(from_region_id) REFERENCES regions(id) ON DELETE SET NULL,
  FOREIGN KEY(to_region_id) REFERENCES regions(id) ON DELETE SET NULL,
  FOREIGN KEY(from_department_id) REFERENCES departments(id) ON DELETE SET NULL,
  FOREIGN KEY(to_department_id) REFERENCES departments(id) ON DELETE SET NULL,
  FOREIGN KEY(assigned_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_asset_assignments_asset ON asset_assignments(asset_id);

CREATE TABLE IF NOT EXISTS asset_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id UUID NOT NULL,
  event_type_code VARCHAR(50),
  description TEXT,
  performed_by UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE,
  FOREIGN KEY(event_type_code) REFERENCES event_types(code) ON DELETE SET NULL,
  FOREIGN KEY(performed_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_asset_events_asset ON asset_events(asset_id);


-- ======================
-- MAINTENANCE: repairs & parts
-- ======================

CREATE TABLE IF NOT EXISTS repairs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id UUID NOT NULL,
  reported_by UUID,
  reported_at TIMESTAMPTZ DEFAULT now(),
  repair_date TIMESTAMPTZ,
  description TEXT,
  performed_by VARCHAR(255),
  status_code VARCHAR(50) DEFAULT 'reported',   -- FK -> repair_statuses
  total_cost NUMERIC(18,2) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  deleted_at TIMESTAMPTZ,
  deleted_by UUID,
  FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE,
  FOREIGN KEY(reported_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY(status_code) REFERENCES repair_statuses(code) ON DELETE SET NULL,
  FOREIGN KEY(deleted_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_repairs_asset ON repairs(asset_id);
CREATE INDEX IF NOT EXISTS idx_repairs_status ON repairs(status_code);

CREATE TABLE IF NOT EXISTS repair_parts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repair_id UUID NOT NULL,
  name VARCHAR(255),
  part_number VARCHAR(255),
  quantity INTEGER DEFAULT 1,
  cost NUMERIC(18,2) DEFAULT 0,
  FOREIGN KEY(repair_id) REFERENCES repairs(id) ON DELETE CASCADE
);

-- Jadval: remont statuslari tarixini saqlash (repair_status_history)
CREATE TABLE IF NOT EXISTS repair_status_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repair_id UUID NOT NULL,
  old_status VARCHAR(50),
  new_status VARCHAR(50),
  changed_by UUID,
  changed_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(repair_id) REFERENCES repairs(id) ON DELETE CASCADE,
  FOREIGN KEY(old_status) REFERENCES repair_statuses(code) ON DELETE SET NULL,
  FOREIGN KEY(new_status) REFERENCES repair_statuses(code) ON DELETE SET NULL,
  FOREIGN KEY(changed_by) REFERENCES users(id) ON DELETE SET NULL
);


-- ======================
-- FINANCE: expenses
-- ======================

CREATE TABLE IF NOT EXISTS expenses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id UUID,
  department_id UUID,
  expense_type_code VARCHAR(50),
  amount NUMERIC(18,2),
  currency VARCHAR(10) DEFAULT 'UZS',
  occurred_at TIMESTAMPTZ DEFAULT now(),
  description TEXT,
  created_by UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE SET NULL,
  FOREIGN KEY(department_id) REFERENCES departments(id) ON DELETE SET NULL,
  FOREIGN KEY(expense_type_code) REFERENCES expense_types(code) ON DELETE SET NULL,
  FOREIGN KEY(created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_expenses_dept ON expenses(department_id);


-- ======================
-- ANALYTICS: forecasts
-- ======================

CREATE TABLE IF NOT EXISTS forecasts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region_id UUID,
  service_id UUID,
  asset_type_id UUID,
  forecast_year INTEGER,
  demand_estimate INTEGER,
  method VARCHAR(100),
  confidence NUMERIC(5,2),
  created_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(region_id) REFERENCES regions(id) ON DELETE SET NULL,
  FOREIGN KEY(service_id) REFERENCES services(id) ON DELETE SET NULL,
  FOREIGN KEY(asset_type_id) REFERENCES asset_types(id) ON DELETE SET NULL
);


-- ======================
-- AUDIT & ATTACHMENTS
-- ======================

CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_user_id UUID,
  action VARCHAR(255),           -- masalan 'UPDATE assets'
  object_table VARCHAR(255),     -- masalan 'assets'
  object_id UUID,                -- usha objectning id si
  old_data JSONB,
  new_data JSONB,
  extra JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(actor_user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_logs(actor_user_id);

-- Polimorf fayl ilovasi: attachments (object_table + object_id)
CREATE TABLE IF NOT EXISTS attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  object_table VARCHAR(255) NOT NULL,
  object_id UUID NOT NULL,
  filename VARCHAR(255),
  url VARCHAR(2048),
  content_type VARCHAR(100),
  created_by UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_attachments_object ON attachments(object_table, object_id);


-- ======================
-- NOTIFICATIONS
-- ======================

CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type VARCHAR(50),
  title VARCHAR(255),
  message TEXT,
  entity_type VARCHAR(100),
  entity_id UUID,
  created_by UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  FOREIGN KEY(created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS notification_recipients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  notification_id UUID NOT NULL,
  user_id UUID NOT NULL,
  is_read BOOLEAN DEFAULT false,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(notification_id, user_id),
  FOREIGN KEY(notification_id) REFERENCES notifications(id) ON DELETE CASCADE,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notification_recipients_user_unread ON notification_recipients(user_id, is_read);


-- ======================
-- SYSTEM SETTINGS (key-value)
-- ======================

CREATE TABLE IF NOT EXISTS system_settings (
  key VARCHAR(255) PRIMARY KEY,
  value JSONB,
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ======================
-- SAMPLE INDEX RECOMMENDATIONS
-- ======================

CREATE INDEX IF NOT EXISTS idx_repairs_reported_by ON repairs(reported_by);
CREATE INDEX IF NOT EXISTS idx_assets_serial ON assets(serial_number);


-- =============================================================
-- END OF SCHEMA
-- Eslatma (Developer notes):
-- - repair_statuses jadvali repairs.status_code bilan bog'langan.
-- - repair_status_history (yoki repair_status_history jadvali) yordamida status o'zgarishlari tarixini saqlang.
-- - attachments polimorfik: object_table/object_id orqali har qanday jadvalga bog'lanadi.
-- - audit_logs har qanday muhim o'zgarishlarni yozib boradi.
-- - Barqarorlik va performance uchun kerakli indekslar qo'shildi; katta hajmlar bo'lsa partitsiyalashni ko'rib chiqing.
-- =============================================================