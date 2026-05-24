# ATV Platformasi — Loyiha infratuzilmasi

## 📌 Bu qanday loyiha?

ATV (Axborot-Texnika Vositalari) — davlat tashkilotlarida texnik vositalarni **markazlashgan boshqarish, monitoring va tahlil** uchun ishlab chiqilgan backend platformasi.

### Asosiy yechiladigan muammolar:

* ✅ Texnik vositalarni yagona reyestrda saqlash
* ✅ Hudud va xizmat kesimida taqsimotni boshqarish
* ✅ Sklad va ehtiyot qismlar nazorati
* ✅ Ta'mirlash jarayonlarini kuzatish
* ✅ Xarajatlarni hisoblash
* ✅ Analitika va prognozlash

---

## 🏗 Arxitektura

Loyiha **Modular Clean Architecture** tamoyillari asosida qurilgan:

```
So'rov → Middleware → API Router → Dependency → Xizmat → Repozitoriy → Ma'lumotlar bazasi
                                    ↓
                              Domain hodisalar
                              (Tarix + Audit + Xabarnomalar)
```

### Ilova qatlamlari

| Qatlam | Vazifasi | Joylashuvi |
|--------|----------|------------|
| **API Layer** | FastAPI routerlar, so'rovlarni tekshirish | `src/api/` |
| **Xizmat Layer** | Biznes logika | `src/services/` |
| **Repozitoriy Layer** | Ma'lumotlarga kirish, SQL so'rovlar | `src/repositories/` |
| **Domen modellar** | SQLAlchemy modellar | `src/db/models/` |
| **Sxemalar** | Pydantic sxemalar | `src/schemas/` |
| **Yadro** | Konfiguratsiya, xavfsizlik, hodisalar | `src/core/` |
| **Middleware** | Audit, logging, metrikalar | `src/middlewares/` |

---

## 🔐 Xavfsizlik tizimi

### Autentifikatsiya

* **JWT** (access + refresh tokenlar)
* Access token — 15 daqiqa (standart)
* Refresh token — 7 kun
* Refresh token rotation (har bir refresh da yangi juftlik yaratiladi)
* Qurilma va IP bog'lash (device binding, IP binding)
* Token qora ro'yxati (Redis production da, xotira dev da)
* Cookie va header orqali autentifikatsiya

### Avtorizatsiya (RBAC + CAC)

**RBAC** (Role-Based Access Control):

| Rol | Tavsif |
|-----|--------|
| `superadmin` | To'liq kirish huquqi |
| `admin` | O'z hududida CRUD amallar |
| `operator` | Ma'lumot kiritish va tahrirlash |
| `approver` | So'rovlarni tasdiqlash |
| `analyst` | Faqat analitikani o'qish |

**CAC** (Context-based Access Control):

* Hudud chegaralari (foydalanuvchi faqat o'z hududini ko'radi)
* Xizmat chegaralari
* Yaratuvchi huquqi (faqat yaratuvchi o'chiradi/tahrirlaydi)
* Ko'p bosqichli tasdiqlash

### Parollar

* Xeshlash: bcrypt (12 rounds)
* SHA-256 normalizatsiya (bcrypt 72 bayt cheklovini chetlab o'tish)

---

## 🔄 Asosiy ma'lumotlar oqimlari

### Aktiv hayot sikli

```
Foydalanuvchi → Aktiv yaratadi → Hudud/omborga topshiradi
     → Kerak bo'lsa ta'mirlash yaratiladi
     → Ombordan ehtiyot qismlar ishlatiladi
     → Harakatlar qayd etiladi
     → Barcha amallar audit jurnaliga yoziladi
     → Xarajatlar hisoblanadi
     → Analitika va prognozlar generatsiya qilinadi
```

### So'rov → Tasdiqlash → Hujjat oqimi

```
So'rov (ariza) → Tasdiqlash (ko'p bosqichli kelishuv)
              → Hujjat (akt/hujjat)
              → Komissiya
              → Topshirish/O'tkazma
```

---

## 📊 Modullar

| Modul | Tavsif | Asosiy endpointlar |
|-------|--------|-------------------|
| **Auth & Foydalanuvchilar** | Autentifikatsiya, sessiyalar, RBAC | `/auth/*`, `/users/*`, `/rbac/*` |
| **Tashkilot** | Hududlar va xizmatlar | `/regions/*`, `/services/*` |
| **Aktivlar** | Texnik vositalar (CRUD, statuslar, o'tkazmalar) | `/assets/*` |
| **Ombor** | Skladlar, ehtiyot qismlar, harakatlar | `/warehouses/*` |
| **Ta'mirlash** | Ta'mirlar va ta'mir ehtiyot qismlari | `/assets/repairs/*` |
| **Xarajatlar** | Moliyaviy xarajatlar | `/expenses/*` |
| **Tasdiqlash** | Arizalar va kelishish | `/approvals/*` |
| **Hujjatlar** | Hujjatlar va fayllar | `/assets/documents/*` |
| **Analitika** | Tahlillar, prognozlar, ogohlantirishlar | `/analytics/*` |
| **Audit** | Amallar audit va striming | `/audit/*` |

---

## 🛠 Texnologik stek

| Komponent | Texnologiya |
|-----------|-------------|
| **Backend Framework** | FastAPI (Python 3.12+) |
| **Ma'lumotlar bazasi** | PostgreSQL |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Migratsiyalar** | Alembic |
| **Kesh / Navbat** | Redis |
| **Fon vazifalar** | Celery |
| **Monitoring** | Prometheus, Sentry |
| **Rate Limiting** | SlowAPI |
| **Admin panel** | SQLAdmin |
| **Konteynerizatsiya** | Docker, docker-compose |

---

## 📁 Loyiha tuzilishi

```
src/
├── api/                    # FastAPI routerlar va bog'liqliklar
│   ├── routers/v1.py       # Asosiy v1 router
│   ├── v1/                 # Modullar bo'yicha routerlar
│   │   ├── auth/           # /auth/*
│   │   ├── users/          # /users/*
│   │   ├── assets/         # /assets/*
│   │   ├── analytics/      # /analytics/*
│   │   ├── audit/          # /audit/*
│   │   └── ...
│   └── dependencies/       # FastAPI Depends
├── core/                   # Ilova yadrosi
│   ├── config.py           # Sozlamalar (Settings)
│   ├── security/           # JWT, parollar, RBAC, qora ro'yxat
│   ├── database/           # Async/sync engine, sessiya
│   ├── exceptions/         # Xatolarni qayta ishlash
│   ├── events/             # Domain hodisalar
│   ├── audit/              # Audit oqimi (xotira/redis)
│   ├── cache/              # Keshlash
│   ├── storage/            # Fayl saqlash
│   ├── notifications/      # Xabarnomalar (DB, WebSocket)
│   ├── observability/      # Prometheus, Sentry
│   ├── admin/              # SQLAdmin konfiguratsiyasi
│   └── lifespan.py         # Startup/shutdown
├── db/                     # Ma'lumotlar bazasi
│   ├── models/             # SQLAlchemy modellar
│   ├── migrations/         # Alembic migratsiyalar
│   ├── base.py             # Base klass
│   ├── mixins.py           # Mixin'lar (UUID, Timestamp, va boshqalar)
│   └── meta.py             # Metama'lumotlar
├── services/               # Biznes logika
├── repositories/           # Ma'lumotlarga kirish
├── schemas/                # Pydantic sxemalar
├── middlewares/            # ASGI middleware
│   ├── audit.py            # So'rovlarni audit qilish
│   ├── logging.py          # Logging
│   ├── metrics.py          # Prometheus metrikalar
│   └── request_id.py       # X-Request-ID
├── tasks/                  # Celery vazifalar
├── scripts/                # CLI skriptlar (bootstrap, tozalash)
├── utils/                  # Yordamchi utilitalar
├── storage/                # Fayl saqlash (mahalliy)
├── static/                 # Statik fayllar (swagger, avatarlar)
└── templates/              # Jinja2 shablonlar (SQLAdmin)
```

---

## 🚀 Ishga tushirish

### Talablar

* Python 3.12+
* PostgreSQL
* Redis (dev uchun ixtiyoriy)
* Docker (ixtiyoriy)

### Tezkor boshlash

```bash
# 1. Klonlash
git clone <repo-url>
cd atv

# 2. Muhit sozlamalari
cp .env-example .env
# .env faylini tahrirlang

# 3. Bog'liqliklarni o'rnatish
uv sync

# 4. Migratsiyalarni qo'llash
uv run alembic -c src/alembic.ini upgrade head

# 5. RBAC seed
uv run python -m scripts.cli bootstrap-rbac

# 6. Superadmin yaratish
uv run python -m scripts.cli create-superadmin

# 7. Serverni ishga tushirish
uv run src/main.py
```

### Docker orqali ishga tushirish

```bash
docker-compose up --build
```

### API hujjatlari

* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

---

## 📈 Middleware Pipeline

Middleware bajarilish tartibi (muhim!):

1. **TrustedHostMiddleware** — ALLOWED_HOSTS tekshiruvi
2. **CORSMiddleware** — CORS sarlavhalari
3. **RequestIDMiddleware** — X-Request-ID traссировka
4. **LoggingMiddleware** — So'rovlarni loglash
5. **AuditMiddleware** — Barcha HTTP so'rovlarni audit qilish
6. **SlowAPIMiddleware** — Rate limiting
7. **MetricsMiddleware** — Prometheus metrikalar (oxirgi)
8. **SessionMiddleware** — SQLAdmin uchun sessiyalar

---

## 📊 Hodisalar tizimi (Domain Events)

Yon ta'sirlar uchun uch bosqichli pipeline:

```
1. HISTORY (muhim) — O'zgarishlar tarixini yozish
2. AUDIT (muhim emas) — Audit oqimiga jo'natish
3. NOTIFICATION (muhim emas) — Xabarnomalarni yuborish
```

Audit va xabarnomalardagi xatolar **biznes operatsiyani buzmaydi**.

---

## 🔧 Konfiguratsiya

Barcha sozlamalar muhit o'zgaruvchilari (`.env`) orqali. Asosiy toifalar:

| Toifa | Tavsif |
|-------|--------|
| `APP_*` | Ilova sozlamalari |
| `POSTGRES_*` | Ma'lumotlar bazasi ulanishi |
| `JWT_*` | Token sozlamalari |
| `REDIS_*` | Redis |
| `CELERY_*` | Celery |
| `SMTP_*` | Email |
| `RATE_LIMIT_*` | Rate limiting |
| `STORAGE_*` | Fayl saqlash |
| `ALERT_*` | Ogohlantirish chegaralari |
| `LOG_*` | Logging |
| `PROMETHEUS_*` / `SENTRY_*` | Monitoring |

---

## 🧪 Testlash

```bash
# Barcha testlarni ishga tushirish
uv run pytest

# Coverage bilan
uv run pytest --cov

# Faqat ma'lum fayl
uv run pytest tests/test_auth.py
```

---

## 📚 Hujjatlar jadvali

| Fayl | Tavsif |
|------|--------|
| `README.md` | Umumiy loyiha tavsifi |
| `docs/PROJECT_OVERVIEW.md` | Rus tilida — infratuzilma |
| `docs/ATV_PLATFORMASI_DATABASE_DOKLADI.MD` | Ma'lumotlar bazasi hujjati |
| `docs/ASSET_MODELS_PREVIEW.MD` | Modellar tavsifi (rus tilida) |
| `docs/UZ/README.md` | Uz tilida umumiy tavsif |
| `docs/UZ/LOYIHA_TASNIFI.md` | **Bu fayl** — infratuzilma |
| `docs/UZ/MA'LUMOTLAR_BAZASI_HISBOTI.md` | Ma'lumotlar bazasi |
| `docs/UZ/ACTIV_MODELLARI_TASNIFI.md` | Aktiv modellar |
| `docs/UZ/RBAC_ROLLAR_TIZIMI.md` | Rollar va ruxsatlar |
| `docs/UZ/TEZKOR_BOSHLOV_QOLLANMASI.md` | Tezkor boshlash |
