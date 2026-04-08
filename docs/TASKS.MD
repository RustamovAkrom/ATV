# ATV Backend: 1 Oylik Aniq Delivery Plan

- Start date: 2026-04-08
- Target handover date: 2026-05-08
- Duration: 4 hafta (20 ish kuni)
- Goal: productionga tayyor, testlangan, dokumentatsiyali backend MVP

## 1) Scope Freeze (nima topshiramiz)

P0 (majburiy, 1 oyda bitishi shart):
- Auth + RBAC
- Users, Regions, Services
- Asset catalog (categories, manufacturers, models, classes)
- Assets lifecycle (create/update/state/history/transfer/assignment)
- Warehouse (warehouses, parts, stock, movements)
- Repairs (repair flow, repair_parts, repair_status_history)
- Expenses
- Request -> Approval -> Document -> Commission asosiy oqimi
- Audit logs
- Basic notifications
- Swagger/OpenAPI to'liq va testlar

P1 (faqat vaqt qolsa):
- Forecast algoritmning kengaytmasi
- Advanced analytics dashboard endpoints
- Background jobs (Celery/Redis)

## 2) Definition of Done (DoD)

Har modul DONE bo'lishi uchun:
- CRUD/flow endpointlar ishlaydi
- request/response schema yozilgan
- service/repository layer ajratilgan
- migration bor
- unit + integration test bor
- permission check qo'yilgan
- audit event yoziladi
- API_SPEC hujjati yangilangan

## 3) Milestone va Deadline

- M1 (2026-04-14): Foundation + Auth + RBAC + Users
- M2 (2026-04-21): Assets domain to'liq
- M3 (2026-04-28): Warehouse + Repairs + Expenses
- M4 (2026-05-05): Request/Document flow + Audit + Notifications + Analytics basic
- Final (2026-05-08): Stabilization, bugfix, release handover

## 4) Haftalar bo'yicha aniq ish rejasi

## WEEK 1 (2026-04-08 -> 2026-04-14): Foundation, Auth, RBAC, Users

W1-01 Project bootstrap
- Task: FastAPI app skeleton, env config, settings, logging, exception handler
- Output: `app/` structure, `.env.example`, start command
- Acceptance: app localda run bo'ladi, `/health` 200

W1-02 Database foundation
- Task: async SQLAlchemy, session, base model, Alembic init
- Output: first migration + migration workflow guide
- Acceptance: `upgrade head` muvaffaqiyatli

W1-03 Auth
- Task: password hashing, JWT access/refresh, login/refresh/logout
- Output: `/auth/*` endpointlar
- Acceptance: login -> token -> protected endpoint chain ishlaydi

W1-04 RBAC
- Task: roles/permissions loading, `require_permission()` dependency
- Output: permission-based access control
- Acceptance: ruxsatsiz user 403 oladi

W1-05 Users
- Task: users CRUD, pagination/filter, soft-delete
- Output: `/users` endpointlari
- Acceptance: create/read/update/delete flow testdan o'tadi

W1-06 Quality gate
- Task: lint/format/test pipeline
- Output: CI config (minimum lint + tests)
- Acceptance: PR check green

## WEEK 2 (2026-04-15 -> 2026-04-21): Assets Core

W2-01 Reference entities
- Task: categories/manufacturers/models/classes CRUD
- Output: reference endpoints + migrations
- Acceptance: unique/check/fk validatsiya ishlaydi

W2-02 Assets CRUD
- Task: create/get list/get by id/update/soft-delete
- Output: filterlar (`region/service/status/search`)
- Acceptance: list endpointda pagination + filter ishlaydi

W2-03 Asset lifecycle logic
- Task: status/lifecycle update, condition update, state history write
- Output: `asset_state_history` avtomatik logikasi
- Acceptance: har status update tarixda aks etadi

W2-04 Transfer/Assignment flow
- Task: `asset_transfers` + `asset_assignments` full workflow
- Output: assign/unassign/transfer endpointlar
- Acceptance: transfer paytida assignment to'g'ri yopilib-yangilanadi

W2-05 Passport va class history
- Task: asset_passport, passport_items, passport_movements, class_history CRUD
- Output: passport API
- Acceptance: assetga 1:1 passport constraint saqlanadi

W2-06 Security/validation gate
- Task: business validations
- Output: clear error contract
- Acceptance: noto'g'ri transfer/status holatlari 4xx qaytaradi

## WEEK 3 (2026-04-22 -> 2026-04-28): Warehouse, Repairs, Expenses

W3-01 Warehouses + parts
- Task: warehouse CRUD, parts CRUD
- Output: `/warehouses`, `/parts`
- Acceptance: FK + status checks to'g'ri

W3-02 Stock engine
- Task: `warehouse_part_stock` update service
- Output: stock calculate/update
- Acceptance: stock manfiyga tushmaydi

W3-03 Movements
- Task: IN/OUT movement transaction
- Output: atomic movement service
- Acceptance: movement yozuvi va stock update bitta transactionda

W3-04 Repairs core
- Task: create/assign/status/complete repair
- Output: `/repairs/*`
- Acceptance: active repair qoidalari ishlaydi

W3-05 Repair parts integration
- Task: repair_parts qo'shish + warehouse deduct + total_cost update
- Output: integrated repair flow
- Acceptance: repair complete bo'lganda cost to'g'ri hisoblanadi

W3-06 Expenses
- Task: expense create/list, asset/repair bog'lash
- Output: `/expenses`
- Acceptance: expense_type + amount validations ishlaydi

## WEEK 4 (2026-04-29 -> 2026-05-08): Flow Integration, Audit, Test, Release

W4-01 Request workflow
- Task: requests + items + approvals + status_history
- Output: approval pipeline endpointlari
- Acceptance: multi-step approval flow end-to-end ishlaydi

W4-02 Documents + signatures + files + commission
- Task: documents lifecycle, signatures, file versioning, asset_commissions
- Output: `/documents/*` + related endpoints
- Acceptance: draft -> pending_sign -> signed holatlari ishlaydi

W4-03 Audit middleware
- Task: write operationlar uchun audit event
- Output: audit middleware/service
- Acceptance: CRUD actionlar `audit_logs`ga yoziladi

W4-04 Notifications basic
- Task: create notification + recipients + read flag
- Output: `/notifications` APIs
- Acceptance: user unread list oladi

W4-05 Analytics basic
- Task: KPI endpointlar (`assets by status`, `repairs stats`, `expenses summary`)
- Output: `/analytics/*` basic
- Acceptance: 3 asosiy KPI endpoint ishlaydi

W4-06 Performance hardening
- Task: query profiling, index migration, N+1 fix
- Output: db tuning migration
- Acceptance: top endpointlar response vaqti barqaror

W4-07 Release readiness
- Task: regression tests, bugfix sprint, release notes, handover docs
- Output: v1.0 release candidate
- Acceptance: smoke test checklist 100% green

## 5) Daily Execution Rules (majburiy)

- Har kuni 2 ta blok:
- Build block (feature implement)
- Verify block (test + bugfix + docs)

- Har task uchun:
- Ticket ID (masalan `W2-04`)
- Owner
- ETA (soatda)
- Status (`todo/in_progress/review/done`)

- Har kechqurun:
- Daily changelog
- Risk log yangilash
- Ertangi top-3 priority

## 6) Test Plan (minimum)

- Unit tests: service layer critical logic
- Integration tests: auth, assets transfer, stock movement, repair complete, request approval
- API smoke tests: barcha P0 modul endpointlari
- Negative tests: permissions, validation, not-found, conflict

Target:
- Coverage minimum 70% service layer
- P0 flowlar uchun 100% smoke pass

## 7) Risk Register va Buffer

Asosiy risklar:
- Schema drift (`database.sql` vs migrations)
- Request/document flow complexity
- Warehouse-repair transaction buglar
- Time sink: analytics/forecast scope creep

Mitigation:
- Week 1 oxirida migration freeze policy
- Har hafta juma kuni integration checkpoint
- Week 4da 3 kunlik bugfix-only buffer

## 8) Final Handover Checklist (2026-05-08)

- P0 endpointlar production configda ishlaydi
- Migrations clean (up/down test)
- API docs yangilangan
- README runbook bor
- Test report biriktirilgan
- Known limitations ro'yxati berilgan
- Release tag va changelog tayyor

## 9) Task Tracking Template

`[W?-??] | Modul | Task | Owner | ETA | Start | End | Status | Blocker | Notes`

Misol:
`[W2-04] | Assets | Transfer + Assignment flow | BE-1 | 10h | 2026-04-17 | 2026-04-18 | in_progress | none | transfer close/open fixed`
