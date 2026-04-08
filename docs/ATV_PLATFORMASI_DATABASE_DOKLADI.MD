# ATV PLATFORMASI DATABASE DOKLADI (AKTUAL)
- Source: [database.sql](../database.sql)
- Holat: ushbu hujjat `database.sql` dagi amaldagi modelga mos

## 1) Qisqa maqsad
ATV platformasi sxemasi quyidagilarni qamrab oladi:
- RBAC va foydalanuvchilar
- Region/service tashkiliy modeli
- Asset katalogi va klassifikatsiya
- Sklad, parts, movementlar
- Asset lifecycle (state, transfer, assignment)
- Repair, expense, task, notification
- Request -> approval -> document -> commission oqimi
- Audit va attachments
- Analytics snapshotlar

## 2) Asosiy biznes oqim
`request -> approvals -> document -> commission -> assignment/transfer -> repair -> expense -> analytics`

Qo'llab-quvvatlovchi oqimlar:
- `users -> roles -> permissions`
- `warehouses -> parts -> stock/movements`
- `audit_logs`, `attachments`

## 3) Modul kesimida jadvallar

### A. RBAC va Security
- `roles`: tizim rollari
- `permissions`: granular huquqlar
- `role_permissions`: role-permission M:N
- `user_statuses`: user status lug'ati

### B. Tashkiliy struktura
- `regions`: hududlar daraxti (`parent_id`)
- `services`: xizmat yo'nalishlari
- `region_services`: region-service M:N

### C. Users
- `users`: login, profil, role/status/region/service/rank, xavfsizlik atributlari
- `ranks`: lavozim/daraja spravochnigi

### D. Asset katalogi
- `asset_categories`: ierarxik kategoriyalar
- `manufacturers`: ishlab chiqaruvchilar
- `asset_models`: model + manufacturer + category + life/warranty
- `asset_classes`: asset klass kodi
- `asset_class_history`: asset klassi tarixi

### E. Hujjatlar va imzolash
- `documents`: hujjat header'i (status, type, request/entity bog'lanishlar)
- `document_signatures`: ko'p imzolovchi jarayon
- `document_files`: hujjat fayllari versiyalari
- `warehouse_documents`: ombor kirim/chiqim hujjat bog'lanishi

### F. Sklad va parts
- `warehouses`: omborlar
- `parts`: ehtiyot qismlar katalogi
- `warehouse_part_stock`: joriy qoldiq
- `warehouse_part_movements`: IN/OUT tarix

### G. Asset lifecycle
- `assets`: asosiy asset registri
- `asset_state_history`: status/lifecycle/condition tarixi
- `asset_transfers`: region/service/warehouse transfer tarixi
- `asset_assignments`: region/service/user ga biriktirish tarixi
- `asset_parts`: asset tarkibidagi parts
- `asset_passports`: asset pasporti (1:1)
- `asset_passport_items`: pasport tarkibi
- `asset_passport_movements`: pasport harakati

### H. Repairs va vendors
- `vendors`: tashqi servis/vendorlar
- `repairs`: ta'mir kartasi
- `repair_parts`: ta'mirda ishlatilgan qismlar
- `repair_status_history`: ta'mir status tarixi

### I. Finance va Ops
- `expenses`: xarajatlar
- `tasks`: operatsion vazifalar
- `notifications`: tizim xabarlari
- `notification_recipients`: kimga yuborilgan/o'qilgan

### J. Request workflow
- `requests`: asosiy so'rov (type/status/step)
- `request_items`: so'rov itemlari
- `request_approvals`: bosqichma-bosqich tasdiqlash
- `request_status_history`: so'rov status tarixi
- `asset_commissions`: hujjat asosida commission fakti

### K. Audit va analytics
- `audit_logs`: harakatlar izi
- `attachments`: universal biriktirma fayllar
- `analytics_snapshots`: periodik KPI agregatlar

## 4) Muhim FK bog'lanishlar
- `users.role_id -> roles.id`
- `users.status_code -> user_statuses.code`
- `users.assigned_region_id -> regions.id`
- `users.assigned_service_id -> services.id`
- `users.rank_id -> ranks.id`

- `asset_models.manufacturer_id -> manufacturers.id`
- `asset_models.category_id -> asset_categories.id`
- `assets.model_id -> asset_models.id`
- `assets.class_code -> asset_classes.code`

- `assets.region_id -> regions.id`
- `assets.service_id -> services.id`
- `assets.current_warehouse_id -> warehouses.id`

- `repairs.asset_id -> assets.id`
- `repairs.vendor_id -> vendors.id`
- `repair_parts.repair_id -> repairs.id`
- `repair_parts.part_id -> parts.id`

- `requests.created_by -> users.id`
- `request_items.request_id -> requests.id`
- `request_approvals.request_id -> requests.id`
- `documents.request_id -> requests.id`

- `document_signatures.document_id -> documents.id`
- `document_files.document_id -> documents.id`
- `asset_commissions.document_id -> documents.id`

## 5) Integrity qoidalari (schema ichida bor)
- Positive/zero checks:
- `quantity > 0` (movements, repair_parts, request_items)
- `amount > 0` (expenses)
- `condition_percent` 0..100
- `failure_count`, `usage_intensity`, `total_cost`, `downtime_hours` >= 0

- Business checks:
- `asset_transfers` da kamida bitta yo'nalish o'zgarishi shart
- `asset_assignments.unassigned_at >= assigned_at`
- `documents.status` qat'iy qiymatlar bilan cheklangan
- `requests.status/request_type/current_step` tekshiruvlari bor
- `status='approved'` bo'lsa `approved_by` va `approved_at` majburiy
- `document_signatures.signature_type` faqat `EDS/PDF`

- Uniqueness:
- `documents.document_number`
- `request_items(request_id, asset_model_id)`
- `asset_commissions(asset_id, document_id)`
- `document_signatures(document_id, signer_id)`
- `document_files(document_id, version)`
- `warehouse_documents(document_id, warehouse_id)`

## 6) Hozirgi modeldagi e'tibor talab qiladigan nuqtalar
1. `asset_class_history.id` da `get_random_uuid()` yozilgan; odatda `pgcrypto` bilan `gen_random_uuid()` ishlaydi.
2. `asset_passports`, `asset_passport_items`, `asset_passport_movements`, `asset_class_history`, `vendors` jadvallarida `IF NOT EXISTS` yo'q.
3. Passport/history blokida FKlar to'liq berilmagan (orphan data xavfi bor).
4. Schema ichida index bloklari yo'q; katta hajmda query performance pasayadi.
5. `TIMESTAMP` va `TIMESTAMP WITH TIME ZONE` aralash ishlatilgan; bir xil standart tavsiya etiladi.

## 7) Tavsiya etilgan amaliy ishlash tartibi
- Transfer:
- `asset_transfers` ga yozish
- old assignment ni yopish (`unassigned_at`)
- yangi assignment ochish
- kerak bo'lsa `documents` + `warehouse_documents`

- Request approval:
- `requests` yaratish
- `request_items` to'ldirish
- `request_approvals` bosqichlarini yuritish
- finalni `request_status_history` ga loglash

- Document signing:
- `documents` (`draft`) yaratish
- `document_signatures` bilan marshrut
- `document_files` ga versiyalar
- yakunda `documents.status = signed`

- Repair lifecycle:
- `repairs` ochish (`reported`)
- status o'zgarishlarini `repair_status_history` ga yozish
- parts sarfini `repair_parts` da yuritish
- xarajatni `expenses` ga tushirish

## 8) Yakuniy xulosa
Amaldagi schema biznes oqimni to'liq qamrab oladi va request/document/repair zanjiri yaxshi ajratilgan. Production oldidan indexlar, passport blokining FKlari, UUID funksiyasi va timezone standartlashuvi albatta mustahkamlanishi kerak.
