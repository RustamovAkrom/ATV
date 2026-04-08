# ATV Platformasi Database Report (Manager Version)

## 1. Executive Summary

Document purpose:
- ATV platforma backendi uchun database modelni biznes va texnik nuqtai nazardan aniq tushuntirish.

Current status:
- Schema core business flowni qamrab oladi.
- Asosiy modullar bo'yicha to'liq ma'lumotlar modeli mavjud.
- Productionga chiqishdan oldin bir nechta texnik mustahkamlash ishlari tavsiya etiladi.

Business value:
- Asset lifecycle bo'yicha to'liq nazorat
- Warehouse va repair jarayonlarining izchil hisobi
- Request/approval/document flow orqali boshqaruv shaffofligi
- Audit-ready arxitektura

## 2. Database Scope (Nimani qamrab oladi)

Schema quyidagi domenlarni yopadi:
- Security: roles, permissions, users
- Organization: regions, services
- Asset catalog: categories, manufacturers, models, classes
- Asset operations: assets, state history, transfers, assignments, passports
- Warehouse: warehouses, parts, stock, movements
- Repairs: repairs, repair parts, repair status history, vendors
- Finance: expenses
- Workflow: requests, approvals, documents, signatures, commissions
- Governance: audit logs, notifications, attachments
- Analytics: snapshot KPI table

## 3. Core Business Data Flow

Primary flow:
`request -> approvals -> document -> commission -> assignment/transfer -> repair -> expense -> analytics`

Supporting flows:
- Access control: `users -> roles -> permissions`
- Inventory control: `warehouses -> parts -> stock/movements`
- Compliance trace: `audit_logs`, `attachments`

## 4. Domain-by-Domain Structure

## 4.1 Security & Access

Tables:
- `roles`
- `permissions`
- `role_permissions`
- `users`
- `user_statuses`
- `ranks`

What this gives the business:
- Markazlashgan ruxsat boshqaruvi
- Har bir endpointni permission bilan himoyalash imkoniyati
- User lifecycle monitoring (status, login metadata, 2FA flags)

## 4.2 Organization Model

Tables:
- `regions` (hierarchical)
- `services`
- `region_services`

What this gives the business:
- Region/service kesimida operatsion tahlil
- Asset va xarajatlarni tashkilot strukturasiga bog'lash

## 4.3 Asset Catalog and Identity

Tables:
- `asset_categories`
- `manufacturers`
- `asset_models`
- `asset_classes`
- `asset_class_history`

What this gives the business:
- Yagona klassifikatsiya
- Model asosida normativ analysis (lifetime, warranty)
- Klass o'zgarishi tarixini saqlash

## 4.4 Asset Lifecycle Operations

Tables:
- `assets`
- `asset_state_history`
- `asset_transfers`
- `asset_assignments`
- `asset_parts`
- `asset_passports`
- `asset_passport_items`
- `asset_passport_movements`

What this gives the business:
- Har bir assetning joriy holati + to'liq tarixi
- Ko'chirish va biriktirishni auditga mos yuritish
- Texnik pasport va tarkibiy elementlarni boshqarish

## 4.5 Warehouse & Inventory

Tables:
- `warehouses`
- `parts`
- `warehouse_part_stock`
- `warehouse_part_movements`
- `warehouse_documents`

What this gives the business:
- Real-time stock visibility
- IN/OUT harakatlarning transaction historysi
- Ombor operatsiyalarini hujjat bilan bog'lash

## 4.6 Repairs and External Vendors

Tables:
- `vendors`
- `repairs`
- `repair_parts`
- `repair_status_history`

What this gives the business:
- Ta'mir jarayonini boshidan oxirigacha kuzatish
- Ichki/tashqi repair xarajatlarini ajratish
- Ishlatilgan qismlar bo'yicha cost traceability

## 4.7 Finance and Operations

Tables:
- `expenses`
- `tasks`
- `notifications`
- `notification_recipients`

What this gives the business:
- Asset/repairga bog'langan xarajat hisobi
- Operatsion task management
- Targeted system notifications

## 4.8 Approval and Documentation Workflow

Tables:
- `requests`
- `request_items`
- `request_approvals`
- `request_status_history`
- `documents`
- `document_signatures`
- `document_files`
- `asset_commissions`

What this gives the business:
- Bosqichma-bosqich tasdiqlash
- Hujjat va imzo lifecycle
- Commission eventlarni hujjat asosida rasmiylashtirish

## 4.9 Audit and Analytics

Tables:
- `audit_logs`
- `attachments`
- `analytics_snapshots`

What this gives the business:
- Compliance uchun harakat izi
- Universal fayl biriktirish
- Rahbariyat uchun agregat KPI snapshotlari

## 5. Data Integrity Controls (Already Implemented)

Implemented controls:
- FK constraints across core flows
- Business checks:
- status va type qiymatlarining cheklanishi
- positive/non-negative numeric checks
- vaqt oralig'i checks (`unassigned_at >= assigned_at`)
- approval consistency checks (`approved` bo'lsa approver/date majburiy)
- Uniqueness rules:
- document number
- request item combination
- document signature uniqueness
- document file version uniqueness
- commission pair uniqueness

Manager implication:
- Data quality manual nazoratga kamroq bog'liq bo'ladi
- Process compliance avtomatik cheklovlar orqali ushlanadi

## 6. Current Gaps / Risks (Important)

Risk 1: Index layer yo'q
- Impact: katta data hajmida endpointlar sekinlashadi
- Priority: High

Risk 2: `asset_class_history.id` default function mismatch (`get_random_uuid`)
- Impact: migration/runtime xatolik ehtimoli
- Priority: High

Risk 3: Ba'zi yangi jadvallar `IF NOT EXISTS`siz yaratilgan
- Impact: re-deploy paytida migration collision
- Priority: Medium

Risk 4: Passport/history blokida FKlar to'liq emas
- Impact: orphan data paydo bo'lish xavfi
- Priority: High

Risk 5: `TIMESTAMP` vs `TIMESTAMP WITH TIME ZONE` aralash
- Impact: vaqt zonasi bo'yicha noaniqlik
- Priority: Medium

## 7. Recommended Hardening Plan (Before Production)

Priority-1 (must do):
- Missing index strategy qo'shish
- UUID default functionni `gen_random_uuid()`ga standartlash
- Passport/history jadvallariga FKlarni to'liq qo'yish
- `IF NOT EXISTS` consistency

Priority-2 (strongly recommended):
- Timezone policy standardization (`TIMESTAMP WITH TIME ZONE`)
- Archival/retention policy for audit and history tables

Priority-3 (optimization):
- Analytics snapshot generation job
- Performance profiling for top read endpoints

## 8. Decision Points for Project Manager

Need PM approval on:
- Production release faqat Priority-1 tugagandan keyin
- P1 analytics/forecast ishlarini month-2ga o'tkazish
- Data governance policy (audit retention, backup cadence)

## 9. Final Assessment

Overall assessment: `Good core model, production-ready after hardening`.

Summary:
- Business processlar to'g'ri modellangan.
- Workflow and compliance layer mavjud.
- Texnik jihatdan 4-5 ta aniq mustahkamlash vazifasi bajarilsa, release xavfi keskin kamayadi.

## 10. Reference

- Main schema: [database.sql](../database.sql)
- Delivery plan: [TASKS.MD](./TASKS.MD)
