# 🏢 SERVICES API SPEC

## 📌 Umumiy tavsif

`Services` — tashkilot ichidagi xizmat yo‘nalishlarini boshqaradi.

Masalan:

* Tergov
* Yo‘l harakati xavfsizligi
* Tezkor-qidiruv
* Aloqa va IT

---

# 🧠 CORE CONCEPT

👉 System 2D ishlaydi:

```text id="dimension"
Region (qayerda) + Service (qaysi faoliyat)
```

---

## Misol

| Region    | Service | Natija                           |
| --------- | ------- | -------------------------------- |
| Toshkent  | Tergov  | Shu hududdagi tergov texnikalari |
| Samarqand | IT      | IT uskunalari                    |

---

# 📦 ENTITY STRUCTURE

```json id="service-response"
{
  "id": "uuid",
  "name": "Tergov",
  "code": "INVEST",
  "description": "Tergov bo‘limi",
  "created_at": "timestamp"
}
```

---

# 🔐 ACCESS CONTROL

| Role       | Access |
| ---------- | ------ |
| superadmin | full   |
| admin      | read   |
| moderator  | read   |
| analyst    | read   |

---

# 🚀 ENDPOINTS

---

## 1. CREATE SERVICE

### POST `/api/v1/services`

```json id="create-service"
{
  "name": "Yo‘l harakati",
  "code": "TRAFFIC",
  "description": "Yo‘l harakati xavfsizligi"
}
```

---

### ⚠️ Validation

* `code` UNIQUE
* `name` UNIQUE

---

## 2. GET SERVICES

### GET `/api/v1/services`

---

### Response

```json id="services-list"
[
  {
    "id": "uuid",
    "name": "Tergov",
    "code": "INVEST"
  }
]
```

---

## 3. GET SINGLE SERVICE

### GET `/api/v1/services/{id}`

---

## 4. UPDATE SERVICE

### PATCH `/api/v1/services/{id}`

---

## 5. DELETE SERVICE

### DELETE `/api/v1/services/{id}`

---

### ⚠️ Logic

* ❌ agar asset bog‘langan bo‘lsa → delete mumkin emas
* ❌ agar region_services da ishlatilsa → delete mumkin emas

---

# 🔗 RELATIONSHIPS

| Table               | Field               |
| ------------------- | ------------------- |
| assets              | service_id          |
| users               | assigned_service_id |
| region_services     | service_id          |
| analytics_snapshots | service_id          |
| expenses            | service_id          |

---

# 🔄 REGION ↔ SERVICE

## M:N relationship

👉 `region_services` jadvali orqali

---

## Endpoint

### POST `/api/v1/regions/{id}/services`

```json id="assign-service"
{
  "service_ids": [
    "uuid1",
    "uuid2"
  ]
}
```

---

### Logic

* regionga service biriktiriladi
* `region_services` ga yoziladi

---

# 📊 ANALYTICS HOOKS

* service → KPI
* service → performance
* service → cost analysis

---

# ⚠️ BUSINESS RULES

1. ❌ duplicate service bo‘lmasligi kerak
2. ❌ service o‘chirilmaydi agar ishlatilayotgan bo‘lsa
3. ✅ regionga bir nechta service bo‘lishi mumkin
4. ✅ analytics region + service bo‘yicha ishlaydi

---

# 🔐 SECURITY

* user faqat o‘z service’ini ko‘radi
* `user_scopes` orqali filter ishlaydi

---

# 🧠 BACKEND IMPLEMENTATION

---

## 🔹 Filtering

```python id="filter-example"
WHERE service_id IN user.allowed_services
```

---

## 🔹 Region + Service filter

```python id="combo-filter"
WHERE region_id = X AND service_id = Y
```

---

# 🚀 FUTURE

* service KPI scoring
* service performance ranking
* service-specific dashboards

---

# 🏁 XULOSA

Bu modul:

✅ systemni 2D qiladi
✅ analyticsni kuchaytiradi
✅ taqsimotni aniqlaydi
✅ boshqaruvni yaxshilaydi

---
