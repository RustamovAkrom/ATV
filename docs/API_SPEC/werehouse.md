# 📦 WAREHOUSE API SPEC

## 📌 Umumiy tavsif

`Warehouse` — barcha texnikalar va ehtiyot qismlarning:

* kirimi (IN)
* chiqimi (OUT)
* qoldig‘i (stock)
* harakati (movements)

ni boshqaradi.

---

# 🧠 CORE CONCEPT

👉 2 ta asosiy entity bor:

1. **Parts (ehtiyot qismlar)**
2. **Assets (tayyor texnika)**

---

## Warehouse boshqaradi:

* parts → `warehouse_part_stock`
* movements → `warehouse_part_movements`
* asset → `assets.current_warehouse_id`

---

# 🔐 ACCESS CONTROL

| Role       | Access              |
| ---------- | ------------------- |
| superadmin | full                |
| admin      | full (scope ichida) |
| moderator  | movement create     |
| analyst    | read only           |

---

# 📦 ENTITY STRUCTURE

---

## Warehouse

```json id="k4q1xw"
{
  "id": "uuid",
  "code": "WH-001",
  "name": "Toshkent Ombor",
  "region": {
    "id": "uuid",
    "name": "Toshkent"
  },
  "manager": {
    "id": "uuid",
    "name": "Ali Valiyev"
  }
}
```

---

## Part Stock

```json id="u9k8am"
{
  "warehouse_id": "uuid",
  "part": {
    "id": "uuid",
    "name": "RAM 16GB"
  },
  "quantity_on_hand": 50,
  "min_quantity": 10
}
```

---

## Movement

```json id="d3x6ot"
{
  "id": "uuid",
  "warehouse_id": "uuid",
  "part_id": "uuid",
  "movement_type": "IN",
  "quantity": 10,
  "reference_type": "purchase",
  "reference_id": "uuid",
  "moved_by": "uuid",
  "moved_at": "timestamp"
}
```

---

# 🚀 ENDPOINTS

---

# 🏭 1. CREATE WAREHOUSE

### POST `/api/v1/warehouses`

```json id="y3k8p1"
{
  "code": "WH-001",
  "name": "Toshkent Ombor",
  "region_id": "uuid",
  "manager_user_id": "uuid"
}
```

---

# 📋 2. GET WAREHOUSES

### GET `/api/v1/warehouses`

---

# 📦 3. GET STOCK

### GET `/api/v1/warehouses/{id}/stock`

---

### Response

```json id="k6t3wr"
[
  {
    "part_id": "uuid",
    "name": "SSD 512GB",
    "quantity": 20,
    "min_quantity": 5
  }
]
```

---

# ⬆️ 4. STOCK IN (KIRIM)

### POST `/api/v1/warehouses/{id}/stock/in`

```json id="n5h2l9"
{
  "part_id": "uuid",
  "quantity": 10,
  "reference_type": "purchase"
}
```

---

### Logic

* `warehouse_part_stock.quantity += quantity`
* `warehouse_part_movements` yoziladi

---

# ⬇️ 5. STOCK OUT (CHIQIM)

### POST `/api/v1/warehouses/{id}/stock/out`

```json id="g8z2np"
{
  "part_id": "uuid",
  "quantity": 5,
  "reference_type": "repair"
}
```

---

### Logic

* ❌ agar quantity yetmasa → error
* `stock -= quantity`
* movement yoziladi

---

# 🔄 6. TRANSFER BETWEEN WAREHOUSES

### POST `/api/v1/warehouses/transfer`

```json id="z4k1jq"
{
  "from_warehouse_id": "uuid",
  "to_warehouse_id": "uuid",
  "part_id": "uuid",
  "quantity": 10
}
```

---

### Logic

* from → OUT
* to → IN
* 2 ta movement yoziladi

---

# 🧩 7. USE PART IN REPAIR

### INTERNAL FLOW

👉 Repair module chaqiradi

---

### Logic

* `warehouse_part_stock` kamayadi
* `repair_parts` yoziladi
* movement → OUT (reference_type = repair)

---

# 🏗 8. ASSEMBLE ASSET

### POST `/api/v1/assets/{id}/assemble`

```json id="8c1kp4"
{
  "parts": [
    {
      "part_id": "uuid",
      "quantity": 2
    }
  ]
}
```

---

### Logic

* parts stockdan olinadi
* `asset_parts` yoziladi
* movement → OUT

---

# 📊 9. LOW STOCK ALERT

### GET `/api/v1/warehouses/{id}/low-stock`

---

### Response

```json id="7kj1xt"
[
  {
    "part_id": "uuid",
    "name": "RAM 16GB",
    "quantity": 2,
    "min_quantity": 5
  }
]
```

---

# 🔗 RELATIONSHIPS

| Field                     | Table   |
| ------------------------- | ------- |
| warehouse.region_id       | regions |
| warehouse.manager_user_id | users   |
| stock.part_id             | parts   |
| movement.part_id          | parts   |
| movement.moved_by         | users   |

---

# ⚠️ BUSINESS RULES

1. ❌ Manfiy stock bo‘lishi mumkin emas
2. ❌ OUT → faqat yetarli stock bo‘lsa
3. ✅ Har harakat log qilinadi
4. ❌ To‘g‘ridan-to‘g‘ri stock update qilish mumkin emas
5. ✅ Faqat movement orqali o‘zgaradi

---

# 🔐 SECURITY

* movement → audit_logs yoziladi
* faqat ruxsat berilgan user bajaradi
* warehouse scope tekshiriladi

---

# 📊 ANALYTICS HOOKS

* stock → availability
* movement → consumption rate
* low stock → alert

---

# 🧠 BACKEND IMPLEMENTATION

Service layer:

* stock_in()
* stock_out()
* transfer()
* reserve_part()

---

# 🚀 FUTURE

* barcode scan
* auto reorder
* supplier integration
