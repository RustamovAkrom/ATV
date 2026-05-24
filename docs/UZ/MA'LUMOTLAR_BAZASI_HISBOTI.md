# 🗄️ ATV Platformasi — Ma'lumotlar Bazasi Hisoboti

## 1. Umumiy ma'lumot

**Hujjat maqsadi:**
- ATV platformasi backendi uchun ma'lumotlar bazasi modelini biznes va texnik nuqtai nazardan tushuntirish

**Joriy holat:**
- ✅ Schema asosiy biznes jarayonlarni qamrab oladi
- ✅ Asosiy modullar bo'yicha to'liq ma'lumotlar modeli mavjud
- ⚠️ Productionga chiqishdan oldin bir nechta texnik mustahkamlash ishlari tavsiya etiladi

**Biznes qiymati:**
- ✅ Aktiv hayot sikli bo'yicha to'liq nazorat
- ✅ Ombor va ta'mirlash jarayonlarining izchil hisobi
- ✅ So'rov/tasdiqlash/hujjat oqimi orqali boshqaruv shaffofligi
- ✅ Audit-ready arxitektura

---

## 2. Ma'lumotlar bazasi qamrovi

Schema quyidagi domenlarni yopadi:

| Domen | Jadvallar |
|-------|----------|
| **Xavfsizlik** | roles, permissions, role_permissions, users, user_statuses, ranks |
| **Tashkilot** | regions (ierarxik), services, region_services |
| **Aktiv katalogi** | categories, manufacturers, models, classes |
| **Aktiv operatsiyalari** | assets, state history, transfers, assignments, passports |
| **Ombor** | warehouses, parts, stock, movements |
| **Ta'mirlash** | repairs, repair parts, repair status history, vendors |
| **Moliya** | expenses |
| **Ish jarayoni** | requests, approvals, documents, signatures, commissions |
| **Boshqaruv** | audit logs, notifications, attachments |
| **Analitika** | snapshot KPI jadvali |

---

## 3. Asosiy biznes ma'lumotlar oqimi

### Birlamchi oqim

```
so'rov → tasdiqlash → hujjat → komissiya → topshirish/o'tkazma → ta'mirlash → xarajat → analitika
```

### Yordamchi oqimlar

**Kirish nazorati:**
```
foydalanuvchilar → rollar → ruxsatlar
```

**Inventarizatsiya nazorati:**
```
omborlar → ehtiyot qismlar → stock/harakatlar
```

**Moslik izi:**
```
audit_logs, attachments
```

---

## 4. Domen bo'yicha tuzilma

### 4.1 Xavfsizlik va kirish

**Jadvallar:**
- `roles` — Rollar
- `permissions` — Ruxsatlar
- `role_permissions` — Rol-ruhsat bog'lanishi
- `users` — Foydalanuvchilar
- `user_statuses` — Foydalanuvchi statuslari
- `ranks` — Unvonlar

**Biznes uchun nima beradi:**
- ✅ Markazlashgan ruxsat boshqaruvi
- ✅ Har bir endpointni ruxsat bilan himoyalash
- ✅ Foydalanuvchi hayotiy siklini monitoring (status, login metama'lumotlari, 2FA belgilar)

---

### 4.2 Tashkilot modeli

**Jadvallar:**
- `regions` (ierarxik tuzilma)
- `services` (xizmatlar)
- `region_services` (hudud-xizmat bog'lanishi)

**Biznes uchun nima beradi:**
- ✅ Hududiy bo'linmalar (viloyat → tuman → bo'lim)
- ✅ Funksional xizmatlar (TerGov, Patrul, Aloqa va h.k.)
- ✅ Foydalanuvchilarni hudud/xizmat bo'yicha filtralash
- ✅ Kirish nazorati (foydalanuvchi faqat o'z hududini ko'radi)

---

### 4.3 Aktivlar (Assets)

**Jadvallar:**
- `assets` — Texnik vositalar (kompyuter, kamera, radiostansiya)
- `asset_models` — Modellarning katalogi
- `manufacturers` — Ishlab chiqaruvchilar
- `asset_categories` — Kategoriyalar
- `asset_classes` — Sinflar

**Asosiy maydonlar:**
| Maydon | Tavsif |
|--------|--------|
| `name` | Aktiv nomi |
| `serial_number` | Seriya/inventar raqami |
| `status` | Holat (active/assigned/in_repair/archived) |
| `owner_id` | Joriy egasi (mas'ul shaxs) |
| `region_id` | Hudud (viloyat) |
| `service_id` | Xizmat (bo'lim) |

**Biznes uchun nima beradi:**
- ✅ Barcha texnik vositalarni hisobga olish
- ✅ Joriy holat va joylashuvni kuzatish
- ✅ Aktiv bilan barcha operatsiyalar tarixi

---

### 4.4 Aktiv harakatlari

**Jadvallar:**
- `asset_assignments` — Aktivni foydalanuvchiga topshirish
- `asset_transfers` — Aktivni hudud/ombor o'rtasida o'tkazish
- `asset_history` — Aktiv tarixi

**AssetAssignment maydonlari:**
| Maydon | Tavsif |
|--------|--------|
| `asset_id` | Aktiv |
| `user_id` | Xodim |
| `assigned_at` | Topshirish sanasi |
| `unassigned_at` | Bo'shatish sanasi |

**AssetTransfer maydonlari:**
| Maydon | Tavsif |
|--------|--------|
| `from_warehouse_id` / `to_warehouse_id` | Qaysi ombordan qaysi omborga |
| `from_service_id` / `to_service_id` | Qaysi xizmatdan qaysi xizmatga |
| `status` | Holat (pending/completed/cancelled) |
| `comment` | Izoh |

**Biznes uchun nima beradi:**
- ✅ Kim hozir texnika uchun mas'ul
- ✅ Topshirishlar tarixi
- ✅ Xodimlarning yuklamasini hisoblash
- ✅ Joylashuvni treking
- ✅ O'tkazmalarni kelishish (approval orqali)

---

### 4.5 Ta'mirlash (Repairs)

**Jadvallar:**
- `repairs` — Ta'mirlar
- `repair_parts` — Ta'mir ehtiyot qismlari
- `repair_status_history` — Ta'mir holati tarixi

**Repair maydonlari:**
| Maydon | Tavsif |
|--------|--------|
| `asset_id` | Aktiv |
| `status` | Holat (reported/in_progress/done/canceled) |
| `description` | Muammo tavsifi |
| `labor_cost` | Ish haqi |

**Biznes uchun nima beradi:**
- ✅ Buzilishlar statistikasi
- ✅ Ta'mir xarajatlarini hisoblash
- ✅ Ishonchsiz texnikani aniqlash

---

### 4.6 Ombor (Warehouse)

**Jadvallar:**
- `warehouses` — Omborlar
- `parts` — Ehtiyot qismlar
- `stock` — Ombor qoldiqlari
- `movements` — Harakatlar

**Biznes uchun nima beradi:**
- ✅ Ehtiyot qismlar hisobi
- ✅ Ombor harakatlarini kuzatish
- ✅ Ta'mirlar uchun qismlarni taqdim etish

---

### 4.7 Moliya (Expenses)

**Jadvallar:**
- `expenses` — Xarajatlar

**Bog'lanishlar:**
- `asset_id` — Aktivga xarajat
- `repair_id` — Ta'mirga xarajat
- `region_id` / `service_id` — Hududiy/xizmat xarajatlari

**Biznes uchun nima beradi:**
- ✅ Aktivlar/hududlar/xizmatlar bo'yicha xarajatlar tahlili
- ✅ Byudjetlashtirish
- ✅ Ehtiyojlarni prognozlash

---

### 4.8 Tasdiqlash (Approvals)

**Jadvallar:**
- `approval_requests` — Tasdiqlash so'rovlari
- `approval_signatures` — Tasdiqlash imzolari
- `commissions` — Komissiyalar

**Nima tasdiqlash talab qiladi:**
- ✅ Aktivni topshirish/o'tkazish
- ✅ Arxivlash/o'chirish
- ✅ Ta'mirlashni yakunlash
- ✅ Omborga o'tkazish

**Qanday ishlaydi:**
1. Foydalanuvchi so'rov yaratadi
2. Tasdiqlovchilar xabarnoma oladi
3. Tasdiqlangandan so'ng amal avtomatik bajariladi

---

### 4.9 Hujjatlar (Documents)

**Jadvallar:**
- `documents` — Hujjatlar
- `document_files` — Hujjat fayllari
- `asset_images` — Aktiv rasmlari

**Biznes uchun nima beradi:**
- ✅ Aktiv formulayari (pasport) elektron ko'rinishda
- ✅ Hujjat skanerlari
- ✅ Kelishuvlar va imzolar

---

### 4.10 Audit va xabarnomalar

**Jadvallar:**
- `audit_logs` — Audit jurnali
- `notifications` — Xabarnomalar
- `attachments` — Ilovalar

**Audit jurnali uchun nima beradi:**
- ✅ Xavfsizlik
- ✅ Hodisalarni tekshirish
- ✅ Talablarga moslik (komissiya tekshiruvlari)

**Xabarnomalar uchun:**
- ✅ Ma'lumotlar bazasi
- ✅ WebSocket (real vaqt rejimi)

---

## 5. Modellararo bog'lanishlar

```
                    ┌─────────────────┐
                    │    Region       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     Service     │
                    └────────┬────────┘
                             │
    ┌────────────────┬───────▼───────┬────────────────┐
    │                │               │                │
┌───▼───┐       ┌───▼───┐       ┌───▼───┐        ┌───▼───┐
│ User  │       │ Asset │       │Expense│        │Document│
└───┬───┘       └───┬───┘       └───────┘        └───────┘
    │               │
    │         ┌─────┼─────┬──────────┬──────────┐
    │         │     │     │          │          │
    │    ┌────▼───┐ │  ┌──▼───┐  ┌───▼───┐  ┌───▼───┐
    │    │Repair  │ │  │Transfer│ │Asset  │  │Asset  │
    │    └────┬───┘ │  └───────┘  │History│  │Image  │
    │         │     │             └───────┘  └───────┘
    │    ┌────▼───┐ │
    │    │Repair  │ │
    │    │Part    │ │
    │    └────────┘ │
    │               │
    └───────────────┘
```

---

## 6. Aktiv formulayari tuzilishi

| Bo'lim | Qayerdan olinadi |
|--------|------------------|
| 1. Komplektatsiya | `AssetComponent` |
| 2. Harakatlar | `AssetTransfer` |
| 3. Kategoriya | `AssetClass` |
| 4. Topshirishlar | `AssetAssignment` |
| 5. Nosozliklar | `Repair` |
| 6. Texnik xizmat | `AssetMaintenance` |
| 7. Komponentlarni almashtirish | `AssetComponentChange` |
| 8. Ta'mirlar | `Repair` + `RepairPart` |
| 9. Tekshiruvlar | `AuditLog` |
| 10. Hujjatlar | `Document` + `AssetImage` |

---

## 7. Tavsiyalar

### 7.1 Xavfsizlik

| Muammo | Tavsiya |
|--------|---------|
| Maydon darajasidagi kirish nazorati yo'q | ABAC (Attribute-Based Access Control) qo'shish |
| MFA/2FA yo'q | TOTP, email, SMS qo'llab-quvvatlash |
| Session отзыв yo'q | Token qora ro'yxati (Redis) |

### 7.2 Samaradorlik

| Muammo | Tavsiya |
|--------|---------|
| Analitika keshlanmagan | Redis kesh (1 soat TTL) |
| Indeksatsiya yetarli emas | Kompozit indekslar qo'shish |
| N+1 so'rov muammosi | Eager loading (selectinload) |

### 7.3 Ma'lumotlar izchilligi

| Muammo | Tavsiya |
|--------|---------|
| Bulk operatsiyalar atomarli emas | `atomic` flag qo'shish |
| O'tkazma holati tekshirilmaydi | State machine qo'shish |
| Audit o'zgarmas emas | Append-only audit log |

---

## 8. Xulosa

**Umumiy tizim salomatligi: 7/10 — YAXSHI, yaxshilash imkoniyatlari bor**

### Kuchli tomonlari:

✅ Toza, yaxshi tashkil etilgan kod bazasi
✅ Async/await pattern'lardan to'g'ri foydalanish
✅ Mustahkam RBAC asosi
✅ Keng qamrovli audit izi
✅ To'g'ri tranzaksiya boshqaruvi
✅ Konkurensiya uchun qator darajasidagi bloklash

### Zaif tomonlari:

⚠️ Ba'zi xavfsizlik bo'shliqlari (maydon darajasidagi kirish, MFA)
⚠️ Analitika keshlash yo'q (samaradorlik xavfi)
⚠️ API javoblari izchil emas
⚠️ Xatolarni qayta ishlash pattern'lari to'liq emas
⚠️ Kuzatuvchanlik cheklangan
⚠️ Biznes metrikalar yo'q

---

## 📞 Qo'shimcha ma'lumot

Batafsil ma'lumot uchun:
- `docs/UZ/README.md` — Umumiy tavsif
- `docs/UZ/LOYIHA_TASNIFI.md` — Loyiha infratuzilmasi
- `docs/UZ/RBAC_ROLLAR_TIZIMI.md` — Rollar tizimi
