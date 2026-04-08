# ATV Platform Backend
![](/assets/analytics_dashboard.jpg)

# REQUEST → DOCUMENT → WAREHOUSE → ASSET → COMMISSION → ASSIGNMENT → REPAIR → HISTORY
## 📌 Overview

ATV (Axborot-Texnika Vositalari) platformasi — bu davlat tashkilotlarida texnik vositalarni **markazlashgan holda boshqarish, monitoring qilish va tahlil qilish** uchun ishlab chiqilayotgan backend tizim.

Platforma quyidagi muammolarni hal qiladi:

* texnik vositalarni yagona reyestrda saqlash
* hudud va xizmat kesimida taqsimotni boshqarish
* sklad (ombor) va ehtiyot qismlar nazorati
* ta’mirlash jarayonlarini kuzatish
* xarajatlarni hisoblash
* analitika va prognozlash

---

## 🏗 Architecture

Tizim **modular clean architecture** asosida quriladi:

```text
Request → API → Service → Repository → Database
```

### Layers:

* **API Layer** — FastAPI routerlar
* **Service Layer** — biznes logika
* **Repository Layer** — DB bilan ishlash
* **Domain Models** — entity va schema

---

## 📦 Core Modules

* **Auth & Users** — autentifikatsiya va RBAC
* **Organization** — regions va services
* **Assets** — texnik vositalar
* **Warehouse** — sklad va parts
* **Repairs** — ta’mir jarayonlari
* **Finance** — xarajatlar
* **Analytics** — prognoz va hisobotlar
* **Audit** — barcha harakatlarni loglash

---

## 🧠 Data Model

Database modeli quyidagi asosiy entity’lardan iborat:

* Users / Roles / Permissions
* Regions / Services
* Assets / Asset Models / Categories
* Warehouses / Parts / Movements
* Repairs / Repair Parts
* Expenses / Forecasts
* Audit Logs

👉 Batafsil: `database.sql`

---

## ⚙️ Tech Stack

* **Backend**: FastAPI
* **Database**: PostgreSQL
* **ORM**: SQLAlchemy 2.0 (async)
* **Migrations**: Alembic
* **Cache / Queue**: Redis (optional)
* **Background Jobs**: Celery (optional)
* **Containerization**: Docker

---

## 🚀 Getting Started

### 1. Clone repository

```bash
git clone https://github.com/<your-username>/atv.git
cd atv
```

### 2. Create environment

```bash
cp .env.example .env
```

### 3. Run with Docker

```bash
docker-compose up --build
```

### 4. API docs

```
http://localhost:8000/docs
```

---

## 📁 Project Structure

```bash
app/
  api/            # FastAPI routers
  core/           # config, security
  models/         # SQLAlchemy models
  schemas/        # Pydantic schemas
  services/       # business logic
  repositories/   # DB access layer
  db/             # session, base
  middleware/     # audit, auth
```

---

## 🔐 RBAC (Roles)

* **superadmin** → full access
* **admin** → region level
* **moderator** → limited operations
* **analyst** → read-only analytics

---

## 🔄 Main Data Flow

```text
User
 → creates Asset
 → asset assigned to region/warehouse
 → repair created if needed
 → parts used from warehouse
 → movements recorded
 → all actions logged in audit_logs
 → expenses calculated
 → analytics & forecast generated
```

---

## 🧪 Development Strategy

Project 1 oy ichida bosqichma-bosqich ishlab chiqiladi:

### Week 1

* Project setup
* Auth + Users

### Week 2

* Assets module

### Week 3

* Warehouse + Repairs

### Week 4

* Audit + Analytics + Optimization

---

## 📚 Documentation

* `database.sql` — database schema
* `ATV_PLATFORMASI_DATABASE_DOKLADI.md` — tizim tavsifi
* `docs/API_SPEC.md` — API endpoints
* `docs/ARCHITECTURE.md` — tizim arxitekturasi
* `docs/TASKS.md` — development plan

---

## 🎯 Goal

Platformaning asosiy maqsadi:

> texnik vositalarni boshqarishni avtomatlashtirish va rahbariyatga faktlarga asoslangan qaror qabul qilish imkonini berish


## Additional instructuions
 + Instructions about API endpoints
    - [API_SPEC](/docs/API_SPEC/)
 + Instructions about completed Tasks
    - [TASKS](/docs/TASKS.MD)
 + Instructions about database structure
    - [ATV_PLATFORMASI_DOKLADI](/docs/ATV_PLATFORMASI_DATABASE_DOKLADI.MD)
