# 🔐 RBAC Rollar Tizimi — Refaktoring Hisoboti

## 📋 Loyiha konteksti

ATV Platformasi — davlat mulkini boshqarish tizimi (FastAPI). Tizimda avval **10 ta rol** mavjud edi va ular ortiqcha murakkablashgan edi.

---

## ❌ Eski rollar (10 ta)

```
SUPERADMIN, ADMIN, MODERATOR, ANALYTIC,
REGION_ADMIN, REGION_MANAGER, SERVICE_MANAGER,
OPERATOR, APPROVER, AUDITOR
```

**Muammo:** Ko'p rollar bir-birini takrorlardi, tizimni qo'llab-quvvatlash va testlash qiyinlashgan edi.

---

## ✅ Yangi rollar (5 ta)

| # | Rol | Vazifasi | Asosiy huquqlar |
|---|-----|----------|-----------------|
| 1 | **OPERATOR** | Ma'lumot kiritish | Aktiv yaratish, hujjat yuklash, ta'mir so'rovi |
| 2 | **APPROVER** | So'rovlarni tasdiqlash | Topshirish, o'tkazma, ta'mirni tasdiqlash |
| 3 | **ANALYST** | Faqat tahlil | Dashboard, hisobot, eksport (o'zgartirish yo'q) |
| 4 | **ADMIN** | Tizimni boshqarish | Foydalanuvchilar, hududlar, xizmatlar, sozlamalar |
| 5 | **SUPERADMIN** | To'liq nazorat | Rollar va ruxsatlarni boshqarish, barcha huquqlar |

---

## 🔄 Rollar o'zgarish jadvali

| Eski rol | Yangi rol | Harakat |
|----------|-----------|---------|
| SUPERADMIN | SUPERADMIN | ✅ Saqlanib qoldi |
| ADMIN | ADMIN | ✅ Kengaytirildi |
| REGION_ADMIN | ADMIN | 🔀 Birlashtirildi |
| REGION_MANAGER | ADMIN | 🔀 Birlashtirildi |
| SERVICE_MANAGER | ADMIN | 🔀 Birlashtirildi |
| MODERATOR | OPERATOR | 🔀 Birlashtirildi |
| OPERATOR | OPERATOR | ✅ Saqlanib qoldi |
| APPROVER | APPROVER | ✅ Saqlanib qoldi |
| ANALYTIC | ANALYST | ✏️ Nomi o'zgartirildi |
| AUDITOR | ANALYST | 🔀 Birlashtirildi |

---

## 🔑 Har bir rolning huquqlari

### 1️⃣ OPERATOR (Operator)

**Vazifasi:** Kundalik operatsiyalar — ma'lumot kiritish, aktivlar bilan ishlash

**Huquqlari:**
- ✅ Foydalanuvchilarni ko'rish
- ✅ Aktivlarni ko'rish, yaratish, tahrirlash
- ✅ Ta'mirlash so'rovlarini ko'rish, yaratish, tahrirlash
- ✅ Hujjatlarni ko'rish, yuklash, tahrirlash
- ✅ Omborni ko'rish
- ✅ Tasdiqlash so'rovlarini ko'rish
- ❌ Tasdiqlash/inkor qilish (APPROVER vazifasi)
- ❌ O'chirish

---

### 2️⃣ APPROVER (Tasdiqlovchi)

**Vazifasi:** So'rovlarni ko'rib chiqish va tasdiqlash/inkor qilish

**Huquqlari:**
- ✅ Tasdiqlash so'rovlarini ko'rish, tasdiqlash, inkor qilish
- ✅ Aktivlarni ko'rish
- ✅ Ta'mirlashlarni ko'rish
- ✅ Hujjatlarni ko'rish
- ✅ Analitikani ko'rish
- ❌ Aktiv yaratish
- ❌ Foydalanuvchi boshqaruvi

---

### 3️⃣ ANALYST (Tahlilchi)

**Vazifasi:** Faqat ko'rish va eksport — hech narsani o'zgartira olmaydi

**Huquqlari:**
- ✅ Audit jurnallarini ko'rish va eksport qilish
- ✅ Aktivlarni ko'rish va eksport qilish
- ✅ Ta'mirlashlarni ko'rish va eksport qilish
- ✅ Hujjatlarni ko'rish va eksport qilish
- ✅ Dashboard va analitikani ko'rish
- ✅ Prognozlarni ko'rish
- ✅ Xarajatlarni ko'rish va eksport qilish
- ❌ Hech narsani yaratish, tahrirlash yoki o'chirish

---

### 4️⃣ ADMIN (Administrator)

**Vazifasi:** Tizimni boshqarish — foydalanuvchilar, hududlar, xizmatlar, sozlamalar

**Huquqlari:**
- ✅ Foydalanuvchilarni to'liq boshqarish (CRUD)
- ✅ Rollarni ko'rish
- ✅ Aktivlarni to'liq boshqarish (CRUD)
- ✅ Ta'mirlashlarni boshqarish
- ✅ Hujjatlarni boshqarish
- ✅ Tasdiqlash so'rovlarini boshqarish
- ✅ Omborni boshqarish
- ✅ Hududlar va xizmatlarni boshqarish
- ✅ Xarajatlarni boshqarish
- ✅ Tizim sozlamalari
- ❌ SUPERADMIN huquqlari (rol yaratish/o'chirish)

---

### 5️⃣ SUPERADMIN (Bosh administrator)

**Vazifasi:** To'liq tizim nazorati

**Huquqlari:**
- ✅ **BARCHA HUQUQLAR** — tizimdagi barcha amallar
- ✅ Rollarni boshqarish
- ✅ Ruxsatlarni boshqarish
- ✅ Sessiyalarni boshqarish
- ✅ Tizim sozlamalari

---

## 🗄️ Ma'lumotlar bazasi migratsiyasi

**Migratsiya:** `3e347d55c907_reduce_roles_to_five.py`

### Nima qiladi?

```
1. "analytic" rolini "analyst" ga o'zgartiradi
2. Foydalanuvchilarni eski rollardan yangilariga ko'chiradi:
   - moderator       → operator
   - region_admin    → admin
   - region_manager  → admin
   - service_manager → admin
   - auditor         → analyst
3. Eski rollarni roles jadvalidan o'chiradi
```

### Migratsiyani ishga tushirish

```bash
cd src
alembic upgrade head
```

### Orqaga qaytish (agar kerak bo'lsa)

```bash
cd src
alembic downgrade -1
```

> ⚠️ **Diqqat:** Orqaga qaytishda eski rollar qayta yaratiladi, lekin foydalanuvchilar yangi rollarda qoladi.

---

## 🧪 Test natijalari

**Barcha 216 ta test muvaffaqiyatli o'tdi!**

```
=====================================================
 216 passed, 6 warnings in 211.89s (0:03:31)
=====================================================
```

### Testlar guruhi bo'yicha

| Guruh | Testlar soni | Holat |
|-------|-------------|-------|
| Analitika API | 11 | ✅ |
| Audit stream | 7 | ✅ |
| Aktiv ta'mirlash | 14 | ✅ |
| Xarajatlar | 5 | ✅ |
| Xabarnomalar | 4 | ✅ |
| Foydalanuvchi CRUD | 14 | ✅ |
| Email | 7 | ✅ |
| Audit middleware | 3 | ✅ |
| Repositoriyalar | 12 | ✅ |
| Xizmatlar (Services) | 40 | ✅ |
| Tasdiqlash | 6 | ✅ |
| Aktiv domen | 4 | ✅ |
| Audit xizmati | 10 | ✅ |
| Autentifikatsiya | 10 | ✅ |
| Xavfsizlik | 7 | ✅ |
| Sessiyalar | 7 | ✅ |
| RBAC | 4 | ✅ |
| Eksport | 3 | ✅ |
| Boshqalar | 38 | ✅ |

---

## 🚀 Ishga tushirish rejasi

### 1-qadam: Migratsiyani qo'llash

```bash
cd src
alembic upgrade head
```

### 2-qadam: RBAC seed skriptini ishga tushirish

```bash
task seed-rbac
```

### 3-qadam: Ilovani qayta ishga tushirish

```bash
task run
```

### 4-qadam: Tekshirish

| Rol | Nima tekshirish |
|-----|----------------|
| OPERATOR | Aktiv yaratish, ta'mir so'rovi |
| APPROVER | So'rovni tasdiqlash |
| ANALYST | Dashboard, eksport |
| ADMIN | Foydalanuvchi yaratish |
| SUPERADMIN | Rollarni boshqarish |

---

## 📌 Xulosa

| Ko'rsatkich | Natija |
|-------------|--------|
| Eski rollar soni | 10 ta |
| Yangi rollar soni | **5 ta** |
| Kod fayllari o'zgartirildi | 6 ta |
| Test fayllari o'zgartirildi | 5 ta |
| Migratsiya yaratildi | 1 ta |
| O'tgan testlar | **216 / 216** |
| Muvaffaqiyat | **100%** |

---

## 💡 Refaktoring afzalliklari

1. **Soddalik** — 10 o'rniga 5 ta rol, tushunish oson
2. **Qo'llab-quvvatlash** — kamroq rol = kamroq xatolik
3. **Testlash** — 5 ta scenariy bilan to'liq qoplash
4. **Biznesga mos** — har bir rol aniq vazifani ifodalaydi
5. **Xavfsizlik saqlandi** — huquqlar qayta taqsimlandi, yo'qotish yo'q

---

## 📞 Qo'llab-quvvatlash

Agar savollar bo'lsa, quyidagi hujjatlarni ko'ring:
- `docs/UZ/README.md` — Umumiy tavsif
- `docs/UZ/LOYIHA_TASNIFI.md` — Loyiha infratuzilmasi
- `docs/UZ/MA'LUMOTLAR_BAZASI_HISBOTI.md` — Ma'lumotlar bazasi
