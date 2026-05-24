# ATV Platforma Backendi

![](/assets/analytics_dashboard.jpg)

## 📌 Loyiha haqida

ATV (Axborot-Texnika Vositalari) platformasi — davlat tashkilotlarida texnik vositalarni **markazlashgan holda boshqarish, monitoring qilish va tahlil qilish** uchun ishlab chiqilgan backend tizim.

### Platforma qanday muammolarni hal qiladi?

* ✅ Texnik vositalarni yagona reyestrda saqlash
* ✅ Hudud va xizmat kesimida taqsimotni boshqarish
* ✅ Sklad (ombor) va ehtiyot qismlar nazorati
* ✅ Ta'mirlash jarayonlarini kuzatish
* ✅ Xarajatlarni hisoblash
* ✅ Analitika va prognozlash

---

## 🏗 Arxitektura

Tizim **modular clean architecture** asosida qurilgan:

```
So'rov → API → Xizmat (Service) → Repozitoriy → Ma'lumotlar bazasi
```

### Qatlamlar:

| Qatlam | Vazifasi | Joylashuvi |
|--------|----------|------------|
| **API** | FastAPI routerlar, so'rovlarni qabul qilish | `src/api/` |
| **Xizmat** | Biznes logika | `src/services/` |
| **Repozitoriy** | Ma'lumotlar bazasi bilan ishlash | `src/repositories/` |
| **Modellar** | SQLAlchemy va Pydantic modellari | `src/db/models/`, `src/schemas/` |

---

## 📦 Asosiy modullar

| Modul | Tavsif |
|-------|--------|
| **Auth & Foydalanuvchilar** | Autentifikatsiya, sessiyalar, RBAC |
| **Tashkilot** | Hududlar (regions) va xizmatlar (services) |
| **Aktivlar** | Texnik vositalar (CRUD, statuslar, o'tkazmalar) |
| **Ombor** | Skladlar, ehtiyot qismlar, harakatlar |
| **Ta'mirlash** | Ta'mir jarayonlari va ehtiyot qismlar |
| **Moliya** | Xarajatlar hisobi |
| **Tasdiqlash** | So'rovlar va kelishish jarayonlari |
| **Hujjatlar** | Elektron hujjatlar va fayllar |
| **Analitika** | Tahlillar, prognozlar, ogohlantirishlar |
| **Audit** | Barcha harakatlarni loglash |

---

## 🧠 Ma'lumotlar modeli

Ma'lumotlar bazasi quyidagi asosiy entity'lardan iborat:

* Foydalanuvchilar / Rollar / Ruxsatlar
* Hududlar / Xizmatlar
* Aktivlar / Aktiv modellari / Kategoriyalar
* Omborlar / Ehtiyot qismlar / Harakatlar
* Ta'mirlashlar / Ta'mir ehtiyot qismlari
* Xarajatlar / Prognozlar
* Audit jurnallari

👉 Batafsil: `docs/UZ/MA'LUMOTLAR_BAZASI_HISBOTI.md`

---

## ⚙️ Texnologik stek

| Komponent | Texnologiya |
|-----------|-------------|
| **Backend** | FastAPI (Python 3.12+) |
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

## 🚀 Ishga tushirish

### Talablar

* [Python](https://www.python.org/downloads/) 3.12+
* [UV](https://docs.astral.sh/uv/)
* [Docker](https://docs.docker.com/get-started/get-docker/)
* [Task](https://taskfile.dev/docs/installation/)

### 1. Repozitoriyni klon qilish

```bash
git clone https://github.com/RustamovAkrom/ATV.git
cd ATV
```

### 2. Muhit yaratish

```bash
cp .env.example .env
```

### 3. Docker orqali ishga tushirish

```bash
docker compose up --build
```

### 4. API hujjatlari

```
http://localhost:8000/docs
```

---

## 📁 Loyiha tuzilishi

```
src/
├── api/                    # FastAPI routerlar
│   ├── routers/v1.py       # Asosiy v1 router
│   ├── v1/                 # Modullar bo'yicha routerlar
│   └── dependencies/       # FastAPI Depends
├── core/                   # Ilova yadrosi
│   ├── config.py           # Sozlamalar
│   ├── security/           # JWT, parollar, RBAC
│   ├── database/           # Ma'lumotlar bazasi
│   └── events/             # Domain hodisalar
├── db/                     # Ma'lumotlar bazasi
│   ├── models/             # SQLAlchemy modellar
│   ├── migrations/         # Alembic migratsiyalar
│   └── base.py             # Base klass
├── services/               # Biznes logika
├── repositories/           # Ma'lumotlar bazasiga kirish
├── schemas/                # Pydantic sxemalar
├── middlewares/            # ASGI middleware
├── tasks/                  # Celery vazifalar
├── scripts/                # CLI skriptlar
└── utils/                  # Yordamchi utilitalar
```

---

## 🔐 RBAC (Rollar va ruxsatlar)

Tizimda **5 ta rol** mavjud:

| Rol | Tavsif | Huquqlar |
|-----|--------|----------|
| **SUPERADMIN** | Bosh administrator | Barcha huquqlar |
| **ADMIN** | Administrator | Foydalanuvchilar, hududlar, xizmatlar boshqaruvi |
| **OPERATOR** | Operator | Aktiv yaratish, ta'mir so'rovlari |
| **APPROVER** | Tasdiqlovchi | So'rovlarni tasdiqlash/inkor qilish |
| **ANALYST** | Tahlilchi | Faqat ko'rish va eksport (o'zgartirish yo'q) |

👉 Batafsil: `docs/UZ/RBAC_ROLLAR_TIZIMI.md`

---

## 🔄 Asosiy ma'lumotlar oqimi

```
Foydalanuvchi
 → Aktiv yaratadi
 → Aktiv hudud/omborga topshiriladi
 → Kerak bo'lsa ta'mirlash yaratiladi
 → Ombordan ehtiyot qismlar ishlatiladi
 → Barcha harakatlar audit jurnallarida qayd etiladi
 → Xarajatlar hisoblanadi
 → Analitika va prognozlar generatsiya qilinadi
```

---

## 🧪 Ishlab chiqish strategiyasi

Loyiha 4 hafta ichida bosqichma-bosqich ishlab chiqildi:

### 1-hafta
* Loyihani sozlash
* Autentifikatsiya + Foydalanuvchilar

### 2-hafta
* Aktivlar moduli

### 3-hafta
* Ombor + Ta'mirlash

### 4-hafta
* Audit + Analitika + Optimallashtirish

---

## 📚 Hujjatlar

| Fayl | Tavsif |
|------|--------|
| `docs/UZ/README.md` | Umumiy tavsif (bu fayl) |
| `docs/UZ/LOYIHA_TASNIFI.md` | Loyiha infratuzilmasi |
| `docs/UZ/MA'LUMOTLAR_BAZASI_HISBOTI.md` | Ma'lumotlar bazasi hujjati |
| `docs/UZ/ACTIV_MODELLARI_TASNIFI.md` | Aktiv modellari tavsifi |
| `docs/UZ/RBAC_ROLLAR_TIZIMI.md` | Rollar va ruxsatlar tizimi |
| `docs/UZ/TEZKOR_BOSHLOV_QOLLANMASI.md` | Tezkor boshlash qo'llanmasi |

---

## 🎯 Maqsad

Platformaning asosiy maqsadi:

> Texnik vositalarni boshqarishni avtomatlashtirish va rahbariyatga faktlarga asoslangan qaror qabul qilish imkonini berish

---

## 📊 Test natijalari

**Barcha 216 ta test muvaffaqiyatli o'tdi!**

```
===================== 216 passed =====================
```

---

## 📞 Aloqa

* GitHub: https://github.com/RustamovAkrom/ATV
* API Docs: http://localhost:8000/docs
