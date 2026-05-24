# 📚 Ma'lumotlar Bazasi Modellari Tavsifi

## 1. 🏗️ Asosiy modellar (Core Models)

### `Asset` — AKTIV (asosiy aktiv)

**Maqsadi:** Tizimning markaziy obyekti — texnik vosita (kompyuter, kamera, radiostansiya va h.k.)

**Asosiy maydonlar:**

| Maydon | Tavsif |
|--------|--------|
| `name` | Aktiv nomi |
| `serial_number` | Seriya/inventar raqami |
| `status` | Holat (active/assigned/in_repair/archived) |
| `owner_id` | Joriy egasi (mas'ul shaxs) |
| `region_id` | Hudud (viloyat) |
| `service_id` | Xizmat (bo'lim) |

**Qayerda ishlatiladi:**
- ✅ Barcha texnik vositalarni hisobga olish
- ✅ Joriy holat va joylashuvni kuzatish
- ✅ Aktiv bilan barcha operatsiyalar tarixi

**Qanday ishlatiladi:**

```python
# Aktiv yaratish
asset = await asset_service.create(data, actor)

# Statusni o'zgartirish
await asset_service.change_status(asset_id, new_status, actor)
```

---

### `AssetModel` — Aktiv modeli

**Maqsadi:** Texnika modellari katalogi

**Asosiy maydonlar:**

| Maydon | Tavsif |
|--------|--------|
| `name` | Model nomi |
| `manufacturer_id` | Ishlab chiqaruvchi |
| `category_id` | Kategoriya |
| `lifetime_years` | Me'yoriy xizmat muddati (yil) |
| `warranty_months` | Kafolat (oy) |

**Qayerda ishlatiladi:**
- ✅ Bir xil turdagi texnikani guruhlash
- ✅ Eshash va almashtirishni prognozlash

---

### `Manufacturer` — Ishlab chiqaruvchi

**Maqsadi:** Texnika ishlab chiqaruvchilar katalogi

**Qayerda ishlatiladi:**
- ✅ Ishlab chiqaruvchilar bo'yicha ishonchlilik tahlili
- ✅ Xaridlarni rejalashtirish

---

## 2. 🔄 Harakat va topshirish modellari

### `AssetAssignment` — Aktiv topshirish

**Maqsadi:** Texnikani xodimlarga topshirishni hisobga olish

**Asosiy maydonlar:**

| Maydon | Tavsif |
|--------|--------|
| `asset_id` | Aktiv |
| `user_id` | Xodim |
| `assigned_at` | Topshirish sanasi |
| `unassigned_at` | Bo'shatish sanasi |

**Qayerda ishlatiladi:**
- ✅ Kim hozir texnika uchun mas'ul
- ✅ Topshirishlar tarixi
- ✅ Xodimlarning yuklamasini hisoblash

**Qanday ishlatiladi:**

```python
# Aktivni xodimga topshirish
await assignment_service.assign_asset(asset_id, user_id, actor)

# Aktivni bo'shatish
await assignment_service.unassign_asset(asset_id, user_id, actor)
```

---

### `AssetTransfer` — Aktiv o'tkazmasi

**Maqsadi:** Texnikani omborlar/xizmatlar o'rtasida o'tkazishni hisobga olish

**Asosiy maydonlar:**

| Maydon | Tavsif |
|--------|--------|
| `from_warehouse_id` / `to_warehouse_id` | Qaysi ombordan/qaysi omborga |
| `from_service_id` / `to_service_id` | Qaysi xizmatdan/qaysi xizmatga |
| `status` | Holat (pending/completed/cancelled) |
| `comment` | Izoh |

**Qayerda ishlatiladi:**
- ✅ Joylashuvni treking
- ✅ O'tkazmalarni kelishish (approval orqali)

---

## 3. 🔧 Texnik xizmat ko'rsatish modellari

### `Repair` — Ta'mirlash

**Maqsadi:** Barcha ta'mirlar va nosozliklarni hisobga olish

**Asosiy maydonlar:**

| Maydon | Tavsif |
|--------|--------|
| `asset_id` | Aktiv |
| `status` | Ta'mir holati (reported/in_progress/done/canceled) |
| `description` | Muammo tavsifi |
| `labor_cost` | Ish haqi |

**Qayerda ishlatiladi:**
- ✅ Buzilishlar statistikasi
- ✅ Ta'mir xarajatlarini hisoblash
- ✅ Ishonchsiz texnikani aniqlash

---

### `RepairPart` — Ta'mir ehtiyot qismlari

**Maqsadi:** Ta'mir vaqtida ishlatilgan ehtiyot qismlarni hisobga olish

**Asosiy maydonlar:**

| Maydon | Tavsif |
|--------|--------|
| `part_name` | Ehtiyot qism nomi |
| `quantity` | Miqdori |
| `unit_price` | Dona narxi |

**Qayerda ishlatiladi:**
- ✅ Ta'mir xarajatlarini batafsil hisoblash
- ✅ Eng ko'p almashtiriladigan qismlarni tahlil qilish

---

### `AssetMaintenance` — Texnik xizmat ko'rsatish (YANGI!)

**Maqsadi:** Rejalashtirilgan texnik xizmat ko'rsatishni hisobga olish

**Asosiy maydonlar:**

| Maydon | Tavsif |
|--------|--------|
| `maintenance_type` | Xizmat turi |
| `performed_at` | O'tkazilgan sana |
| `issues_found` | Aniqlangan muammolar |
| `performed_by_id` | Kim o'tkazgan |

**Qayerda ishlatiladi:**
- ✅ Texnikani o'z vaqtida xizmat ko'rsatish
- ✅ Xizmat muddatini uzaytirish
- ✅ Profilaktika ishlari hujjatlashtirish

---

## 4. 📦 Komplektatsiya modellari

### `AssetComponent` — Aktiv komponentlari (YANGI!)

**Maqsadi:** Aktiv qanday qismlardan tashkil topganini hisobga olish

**Asosiy maydonlar:**

| Maydon | Tavsif |
|--------|--------|
| `name` | Komponent nomi |
| `serial_number` | Komponent seriya raqami |
| `quantity` | Miqdori |

**Qayerda ishlatiladi:**
- ✅ Aktiv formulayari (pasport)
- ✅ Qabul/qayd etish vaqtida komplektlik tekshiruvi
- ✅ Alohida komponentlarni almashtirish

---

### `AssetComponentChange` — Komponent almashtirish (YANGI!)

**Maqsadi:** Aktiv qismlarini almashtirishni hisobga olish

**Asosiy maydonlar:**

| Maydon | Tavsif |
|--------|--------|
| `old_component` | Eski komponent |
| `new_component` | Yangi komponent |
| `reason` | Almashtirish sababi |
| `changed_by_id` | Kim almashtirgan |

**Qayerda ishlatiladi:**
- ✅ Komponent almashtirish tarixi
- ✅ Eng ko'p almashtiriladigan qismlarni tahlil qilish
- ✅ Ehtiyot qismlar xaridini rejalashtirish

---

## 5. 🏢 Tashkilot tuzilmasi

### `Region` — Hudud

**Maqsadi:** Ma'muriy-hududiy birlik (viloyat → tuman → bo'lim)

**Xususiyatlari:**
- ✅ Ierarxik tuzilma (parent_id)
- ✅ Geo-ma'lumotlarni qo'llab-quvvatlash (latitude, longitude, geojson)

**Qayerda ishlatiladi:**
- ✅ Hudud bo'yicha ma'lumotlarni filtrlash
- ✅ Hududiy tahlil
- ✅ Kirish nazorati (foydalanuvchi faqat o'z hududini ko'radi)

---

### `Service` — Xizmat/Yo'nalish

**Maqsadi:** Funksional bo'linma (TerGov, Patrul, Aloqa va h.k.)

**Qayerda ishlatiladi:**
- ✅ Xizmat bo'yicha filtrlash
- ✅ Yo'nalishlar bo'yicha yuklama tahlili

---

## 6. 👤 Foydalanuvchilar va xavfsizlik

### `User` — Foydalanuvchi

**Maqsadi:** Tizim xodimi

**Muhim maydonlar:**

| Maydon | Tavsif |
|--------|--------|
| `role_id` | Rol (SUPERADMIN, ADMIN, OPERATOR va h.k.) |
| `assigned_region_id` | Bog'langan hudud |
| `assigned_service_id` | Bog'langan xizmat |

**Xususiyatlari:**
- ✅ `slug` avtomatik ravishda `login` dan yaratiladi
- ✅ Ma'lumotlarga kirishda hudud/xizmat tekshiriladi

---

### `Role` / `Permission` — Rollar va ruxsatlar

**Maqsadi:** Kirishni boshqarish (RBAC)

**Qanday ishlaydi:**
- ✅ Rollar bir nechta ruxsatlarga ega (permissions)
- ✅ Foydalanuvchi o'z roli orqali huquqlarni oladi
- ✅ Alohida huquqlar ham mumkin (direct_permissions)

---

## 7. 📄 Hujjatlar va rasmlar

### `Document` — Hujjat

**Maqsadi:** Biriktirilgan fayllarni saqlash (formulayarlar, hisob-fakturalar, aktlar)

**Qayerda ishlatiladi:**
- ✅ Aktiv formulayari (pasport) elektron ko'rinishda
- ✅ Hujjat skanerlari
- ✅ Kelishuvlar va imzolar

---

### `DocumentFile` — Hujjat fayli

**Maqsadi:** Hujjatga biriktirilgan fayllar

**Xususiyatlari:**
- ✅ Bir hujjatga bir nechta fayl
- ✅ Hujjat o'chirilganda kaskadli o'chirish

---

### `AssetImage` — Aktiv rasmi

**Maqsadi:** Texnika rasmlari

**Xususiyatlari:**
- ✅ Bir aktivga bir nechta rasm
- ✅ Asosiy rasm (is_primary)
- ✅ Tartiblash imkoniyati (sort_order)

---

## 8. 📊 Hisob va analitika

### `Expense` — Xarajat

**Maqsadi:** Moliyaviy xarajatlarni hisobga olish

**Bog'lanishlar:**
- `asset_id` — Aktivga xarajat
- `repair_id` — Ta'mirga xarajat
- `region_id` / `service_id` — Hududiy/xizmat xarajatlari

**Qayerda ishlatiladi:**
- ✅ Aktivlar/hududlar/xizmatlar bo'yicha xarajatlar tahlili
- ✅ Byudjetlashtirish
- ✅ Ehtiyojlarni prognozlash

---

### `AuditLog` — Audit jurnali

**Maqsadi:** Tizimdagi barcha harakatlarni yozish

**Qayerda ishlatiladi:**
- ✅ Xavfsizlik
- ✅ Hodisalarni tekshirish
- ✅ Talablarga moslik (komissiya tekshiruvlari)

---

### `Notification` — Xabarnoma

**Maqsadi:** Foydalanuvchilarni xabardor qilish

**Yetkazib berish kanallari:**
- ✅ Ma'lumotlar bazasi
- ✅ WebSocket (real vaqt rejimi)

---

## 9. ⚙️ Tizim modellari

### `ApprovalRequest` — Tasdiqlash so'rovi

**Maqsadi:** Muhim harakatlarni kelishish

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

### `RefreshToken` — Yangilash tokeni

**Maqsadi:** Sessiyalarni va JWT tokenlarni boshqarish

**Qayerda ishlatiladi:**
- ✅ Tizimdan xavfsiz chiqish
- ✅ Sessiyalarni bekor qilish
- ✅ Token o'g'irlanishidan himoya

---

## 📊 Modellararo bog'lanishlar diagrammasi

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

## 🎯 Xulosa: Aktiv formulayari quyidagilardan tashkil topadi

| Bo'lim | Ma'lumot manbai |
|--------|----------------|
| 1. Komplektatsiya | `AssetComponent` |
| 2. Harakatlar | `AssetTransfer` |
| 3. Kategoriya | `AssetClass` |
| 4. Topshirishlar | `AssetAssignment` |
| 5. Nosozliklar | `Repair` |
| 6. Texnik xizmat | `AssetMaintenance` |
| 7. Komponent almashtirish | `AssetComponentChange` |
| 8. Ta'mirlar | `Repair` + `RepairPart` |
| 9. Tekshiruvlar | `AuditLog` |
| 10. Hujjatlar | `Document` + `AssetImage` |

---

## 📚 Qo'shimcha ma'lumot

Batafsil ma'lumot uchun:
- `docs/UZ/MA'LUMOTLAR_BAZASI_HISBOTI.md` — Ma'lumotlar bazasi to'liq hisoboti
- `docs/UZ/LOYIHA_TASNIFI.md` — Loyiha infratuzilmasi
- `database.sql` — SQL schema
