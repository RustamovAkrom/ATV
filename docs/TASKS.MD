# ATV Backend Development Plan (1 Month)

## 🎯 Goal

1 oy ichida:

* production-ready backend
* clean architecture
* fully working core modules

---

# 📅 WEEK 1 — FOUNDATION (CRITICAL)

## 1. Project Setup

* [ ] Git structure yaratish
* [ ] Virtual environment (poetry / venv)
* [ ] FastAPI project init
* [ ] Folder structure:

```bash
app/
  api/
  core/
  db/
  models/
  schemas/
  services/
  repositories/
  middleware/
```

* [ ] .env configuration
* [ ] config loader (pydantic settings)

---

## 2. Database Setup

* [ ] PostgreSQL connection (async)
* [ ] SQLAlchemy 2.0 setup
* [ ] Base model (DeclarativeBase)
* [ ] Alembic init
* [ ] First migration run

---

## 3. Core Infrastructure

* [ ] DB session dependency
* [ ] Base repository class
* [ ] Exception handling system
* [ ] Logging setup

---

## 4. Auth System (MVP)

* [ ] User model implement
* [ ] Password hashing (bcrypt)
* [ ] JWT (access + refresh)
* [ ] Login endpoint
* [ ] Token validation dependency

---

## 5. RBAC (IMPORTANT)

* [ ] roles table integration
* [ ] permissions logic
* [ ] dependency:

```python
require_permission("assets.read")
```

* [ ] Role check middleware

---

## 6. Users Module

* [ ] Create user
* [ ] Get user list (pagination)
* [ ] Get user by id
* [ ] Update user
* [ ] Soft delete

---

# 📅 WEEK 2 — ASSETS (CORE DOMAIN)

## 1. Reference Data

* [ ] categories CRUD
* [ ] manufacturers CRUD
* [ ] models CRUD

---

## 2. Assets CRUD

* [ ] Create asset

* [ ] Get list (filters):

  * region
  * service
  * status
  * search

* [ ] Get by id

* [ ] Update asset

* [ ] Soft delete

---

## 3. Asset State Logic

* [ ] status update endpoint
* [ ] lifecycle calculation (auto)
* [ ] condition_percent update

---

## 4. History (CRITICAL)

* [ ] asset_state_history write on update
* [ ] asset_transfers write

---

## 5. Validation Rules

* [ ] asset faqat:

  * warehouse yoki regionda bo‘lishi
* [ ] unique serial_number

---

# 📅 WEEK 3 — WAREHOUSE + REPAIRS

## 1. Warehouse Module

* [ ] warehouse CRUD
* [ ] parts CRUD

---

## 2. Stock System

* [ ] warehouse_part_stock logic
* [ ] initial stock insert

---

## 3. Movements (CRITICAL)

* [ ] IN movement
* [ ] OUT movement
* [ ] transaction (IMPORTANT)

Flow:

```text
movement → validate → update stock → save movement
```

* [ ] negative stock check

---

## 4. Asset ↔ Parts

* [ ] attach parts to asset
* [ ] update quantity

---

## 5. Repairs Module

* [ ] create repair
* [ ] assign repair
* [ ] update status

---

## 6. Repair Logic

* [ ] add parts to repair
* [ ] deduct from warehouse
* [ ] calculate total_cost

---

## 7. Repair History

* [ ] repair_status_history write

---

# 📅 WEEK 4 — FINALIZATION

## 1. Audit System (CRITICAL)

* [ ] middleware:

```text
request → capture → response → log
```

* [ ] audit_logs insert (async)

---

## 2. Expenses

* [ ] create expense
* [ ] link to:

  * asset
  * repair

---

## 3. Analytics (MVP)

* [ ] assets count by region
* [ ] assets by status
* [ ] repair statistics
* [ ] expenses summary

---

## 4. Forecast (Simple)

* [ ] basic прогноз:

  * avg lifetime
  * failure rate

---

## 5. Notifications (Basic)

* [ ] create notification
* [ ] assign to users

---

## 6. Performance Optimization

* [ ] indexes check
* [ ] query optimization
* [ ] N+1 fix

---

## 7. Testing

* [ ] basic API tests
* [ ] auth tests
* [ ] core flows test

---

## 8. Final Cleanup

* [ ] remove unused code
* [ ] consistent naming
* [ ] docstrings

---

# 🧠 DEVELOPMENT RULES (MANDATORY)

## ❗ 1. Har endpointdan oldin:

* request schema
* response schema

---

## ❗ 2. Har write operation:

* transaction ishlat

---

## ❗ 3. Har update:

* history yoz

---

## ❗ 4. Hech qachon:

* business logic router ichida yozma
* faqat service layer

---

## ❗ 5. Har modul:

* api/
* service/
* repository/
* schemas/

---

# ⚠️ COMMON MISTAKES (DON'T DO)

* [ ] fat controllers
* [ ] raw SQL everywhere
* [ ] no validation
* [ ] no transactions
* [ ] no audit

---

# 🏁 FINAL CHECKLIST

* [ ] Auth ishlaydi
* [ ] RBAC ishlaydi
* [ ] Assets CRUD ishlaydi
* [ ] Warehouse logic ishlaydi
* [ ] Repairs flow ishlaydi
* [ ] Audit ishlaydi
* [ ] Analytics basic ishlaydi

---

# 🚀 RESULT

Agar hammasi bajarilsa:

👉 sen qo‘lingda bo‘ladi:

* production-ready backend
* scalable architecture
* real startup-level system
