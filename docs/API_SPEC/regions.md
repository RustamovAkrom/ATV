# 🌍 REGIONS API SPEC

## 📌 Umumiy tavsif

`Regions` — tizimdagi hududiy ierarxiyani boshqaradi.

Bu modul orqali:

* mamlakat → viloyat → tuman → bo‘linma
* xarita (map)
* access scope

boshqariladi.

---

# 🧠 CORE CONCEPT

👉 Regions daraxt (tree structure):

```text id="tree-structure"
Respublika
 ├── Viloyat
 │    ├── Tuman
 │    │    ├── Bo‘linma
```

---

## Field: level

| Level | Ma’nosi    |
| ----- | ---------- |
| 1     | Respublika |
| 2     | Viloyat    |
| 3     | Tuman      |
| 4     | Bo‘linma   |

---

# 📦 ENTITY STRUCTURE

```json id="region-response"
{
  "id": "uuid",
  "name": "Toshkent viloyati",
  "code": "TOS",
  "level": 2,
  "parent_id": "uuid",
  "latitude": 41.3111,
  "longitude": 69.2797,
  "geojson": {},
  "created_at": "timestamp"
}
```

---

# 🌍 GEO DATA (MUHIM)

## latitude / longitude

👉 map marker uchun

---

## geojson

👉 region shape (polygon)

Misol:

```json id="geojson-example"
{
  "type": "Polygon",
  "coordinates": [...]
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

## 1. CREATE REGION

### POST `/api/v1/regions`

```json id="create-region"
{
  "name": "Yunusobod tumani",
  "code": "YUN",
  "level": 3,
  "parent_id": "uuid",
  "latitude": 41.33,
  "longitude": 69.28
}
```

---

### ⚠️ Validation

* parent level +1 bo‘lishi kerak
* code UNIQUE

---

## 2. GET REGIONS (TREE)

### GET `/api/v1/regions/tree`

---

### Response

```json id="tree-response"
[
  {
    "id": "uuid",
    "name": "Toshkent",
    "children": [
      {
        "id": "uuid",
        "name": "Yunusobod",
        "children": []
      }
    ]
  }
]
```

---

## 3. GET REGIONS LIST

### GET `/api/v1/regions`

### Query params

```text id="region-filters"
level
parent_id
search
```

---

## 4. GET SINGLE REGION

### GET `/api/v1/regions/{id}`

---

## 5. UPDATE REGION

### PATCH `/api/v1/regions/{id}`

---

## 6. DELETE REGION

### DELETE `/api/v1/regions/{id}`

---

### ⚠️ Logic

* ❌ agar child mavjud bo‘lsa → delete mumkin emas
* ❌ agar asset bog‘langan bo‘lsa → delete mumkin emas

---

# 🔗 RELATIONSHIPS

| Table               | Field                  |
| ------------------- | ---------------------- |
| regions             | parent_id → regions.id |
| assets              | region_id              |
| warehouses          | region_id              |
| users               | assigned_region_id     |
| analytics_snapshots | region_id              |

---

# 🧠 BUSINESS RULES

1. ❌ cyclic hierarchy bo‘lmasligi kerak
2. ❌ parent → child level noto‘g‘ri bo‘lmasligi kerak
3. ❌ root (respublika) o‘chirib bo‘lmaydi
4. ✅ har region unique codega ega

---

# 📊 ANALYTICS HOOKS

* region → map visualization
* region → KPI aggregation
* region → filtering

---

# 🔐 SECURITY

* region scope userga biriktiriladi (`user_scopes`)
* user faqat o‘z regionini ko‘ra oladi

---

# 🧠 BACKEND IMPLEMENTATION

---

## 🔹 Tree query

* recursive query (CTE)
* yoki nested structure build qilish

---

## 🔹 Scope filtering

```python id="scope-example"
WHERE region_id IN user.allowed_regions
```

---

## 🔹 Geo support

* PostGIS (optional future)
* JSONB geojson (current)

---

# 🚀 FUTURE

* GIS integration (PostGIS)
* heatmap
* region performance scoring

---

# 🏁 XULOSA

Bu modul:

✅ barcha data’ni bog‘laydi
✅ analytics uchun asos
✅ access control uchun asos
✅ map uchun asos

---
