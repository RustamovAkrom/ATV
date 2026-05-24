# 🚀 ATV Platformasi — Tezkor Boshlash Qo'llanmasi

## 📌 Bu nima?

ATV (Axborot-Texnika Vositalari) — davlat tashkilotlarida texnik vositalarni boshqarish uchun backend platformasi.

---

## ⚡ 5 daqiqada ishga tushirish

### 1. Talablar

```
✅ Python 3.12+
✅ PostgreSQL
✅ Redis (ixtiyoriy)
✅ Docker (ixtiyoriy)
```

### 2. O'rnatish

```bash
# Repozitoriyni klonlash
git clone https://github.com/RustamovAkrom/ATV.git
cd ATV

# Muhit sozlamalari
cp .env.example .env
# .env faylini tahrirlang

# Bog'liqliklarni o'rnatish
uv sync
```

### 3. Ma'lumotlar bazasini sozlash

```bash
# Migratsiyalarni qo'llash
cd src
alembic upgrade head

# Rollar va ruxsatlarni yaratish (seed)
uv run python -m scripts.cli bootstrap-rbac

# Superadmin yaratish
uv run python -m scripts.cli create-superadmin
```

### 4. Serverni ishga tushirish

```bash
# Oddiy ishga tushirish
uv run src/main.py

# Yoki
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 5. Tekshirish

```
✅ API docs: http://localhost:8000/docs
✅ ReDoc:    http://localhost:8000/redoc
✅ Admin:    http://localhost:8000/admin
```

---

## 🐳 Docker orqali ishga tushirish

```bash
# Barcha xizmatlarni ishga tushirish
docker compose up --build

# Faqat ma'lumotlar bazasi
docker compose up -d postgres redis
```

---

## 🧪 Testlarni ishga tushirish

```bash
# Barcha testlar
uv run pytest

# Coverage bilan
uv run pytest --cov

# Faqat ma'lum fayl
uv run pytest tests/test_auth.py -v
```

---

## 📂 Loyiha strukturasi (qisqacha)

```
src/
├── api/v1/           # API endpointlar
├── services/         # Biznes logika
├── repositories/     # Ma'lumotlar bazasi
├── db/models/        # SQLAlchemy modellar
├── schemas/          # Pydantic sxemalar
├── core/security/    # JWT, RBAC
└── middlewares/      # Audit, logging
```

---

## 🔑 Asosiy API endpointlar

| Endpoint | Tavsif | Rol |
|----------|--------|-----|
| `POST /auth/login` | Tizimga kirish | Barcha |
| `GET /users/me` | Profil ma'lumotlari | Barcha |
| `GET /assets/` | Aktivlar ro'yxati | Barcha |
| `POST /assets/` | Aktiv yaratish | OPERATOR, ADMIN |
| `POST /approvals/{id}/approve` | So'rovni tasdiqlash | APPROVER |
| `GET /analytics/dashboard` | Dashboard | ANALYST, ADMIN |
| `POST /users/` | Foydalanuvchi yaratish | ADMIN |
| `POST /rbac/roles` | Rol yaratish | SUPERADMIN |

---

## 🛠 Asosiy buyruqlar (Task)

```bash
# Testlarni ishga tushirish
task test

# Ma'lumotlar bazasini migratsiya qilish
task migrate

# Yangi migratsiya yaratish
task makemigrations name=yangi_migratsiya

# RBAC seed
task seed-rbac

# Superadmin yaratish
task create-superadmin

# Ilovani ishga tushirish
task run

# Lint va format
task lint
task format
```

---

## 🔐 Rollar va huquqlar (yangi — 5 ta)

| Rol | Nima qila oladi |
|-----|-----------------|
| **OPERATOR** | Aktiv yaratish, ta'mir so'rovi, hujjat yuklash |
| **APPROVER** | So'rovlarni tasdiqlash/inkor qilish |
| **ANALYST** | Faqat ko'rish: dashboard, hisobot, eksport |
| **ADMIN** | Foydalanuvchilar, hududlar, xizmatlar boshqaruvi |
| **SUPERADMIN** | Barcha huquqlar, rollarni boshqarish |

---

## 🐛 Tez-tez uchraydigan muammolar

### 1. PostgreSQL ulanmadi

```
Error: connection refused
```

**Yechim:**
```bash
# Docker orqali PostgreSQL ishga tushirish
docker compose up -d postgres

# Yoki .env faylida POSTGRES_URL ni tekshiring
```

### 2. Migratsiya xatosi

```
Error: Target database is not up to date
```

**Yechim:**
```bash
cd src
alembic upgrade head
```

### 3. Modul topilmadi

```
ModuleNotFoundError: No module named 'xxx'
```

**Yechim:**
```bash
uv sync
```

---

## 📞 Yordam va qo'llab-quvvatlash

| Manba | Havola |
|-------|--------|
| GitHub | https://github.com/RustamovAkrom/ATV |
| API Docs | http://localhost:8000/docs |
| Admin Panel | http://localhost:8000/admin |

---

## 📚 Batafsil hujjatlar

| Fayl | Tavsif |
|------|--------|
| `docs/UZ/README.md` | Umumiy tavsif |
| `docs/UZ/LOYIHA_TASNIFI.md` | Loyiha infratuzilmasi |
| `docs/UZ/MA'LUMOTLAR_BAZASI_HISBOTI.md` | Ma'lumotlar bazasi |
| `docs/UZ/ACTIV_MODELLARI_TASNIFI.md` | Aktiv modellar |
| `docs/UZ/RBAC_ROLLAR_TIZIMI.md` | Rollar tizimi |
| `docs/UZ/TEZKOR_BOSHLOV_QOLLANMASI.md` | **Bu fayl** — tezkor boshlash |

---

## ✅ Ishga tushirish cheklisti

- [ ] Python 3.12+ o'rnatilgan
- [ ] PostgreSQL ishlayapti
- [ ] `.env` fayli sozlangan
- [ ] `uv sync` bajarilgan
- [ ] Migratsiyalar qo'llangan
- [ ] RBAC seed bajarilgan
- [ ] Superadmin yaratilgan
- [ ] Server ishga tushgan
- [ ] `/docs` sahifasi ochiladi

---

**Tayyor! Platforma ishga tushdi!** 🎉
