# ATV Backend Delivery Plan (Manager Version)

## 1. Executive Summary

Project: ATV Platform Backend
Timeline: 30 calendar days (2026-04-08 -> 2026-05-08)
Delivery Target: Production-ready MVP backend with core operational flows.

Business Outcome:
- Yagona texnika reyestri va asset lifecycle boshqaruvi
- Ombor/parts/repair jarayonlarini to'liq nazorat
- Ruxsat (request) va hujjatlashtirish oqimini avtomatlashtirish
- Auditga tayyor operatsion tizim

Success Criteria (top-level):
- P0 scope 100% delivered
- Critical flowlar (Auth, Asset, Warehouse, Repair, Request/Document) end-to-end working
- API test suite passes
- Handover documentation complete

## 2. Scope and Priorities

P0 (Must-have, contractual delivery scope):
- Auth + RBAC
- Users, Regions, Services
- Asset Catalog + Assets Lifecycle
- Warehouse + Stock + Movements
- Repairs + Repair Parts + Repair History
- Expenses
- Request -> Approval -> Document -> Commission flow
- Audit logs
- Basic notifications
- OpenAPI/Swagger + test coverage baseline

P1 (Time-permitting):
- Advanced analytics
- Forecast enhancements
- Background jobs (Redis/Celery)

Out of scope for Month-1:
- Complex BI dashboards
- Full event-driven microservices refactor
- Multi-tenant split architecture

## 3. Delivery Milestones (Dates and Outputs)

### M1 — Foundation Complete (Due: 2026-04-14)
Deliverables:
- FastAPI base architecture
- DB setup + Alembic migrations
- Auth endpoints (login/refresh)
- RBAC permission checks
- Users module CRUD

Exit Criteria:
- `/health` works
- Auth flow validated
- Permission denied scenarios return 403
- Initial CI checks green

### M2 — Asset Domain Complete (Due: 2026-04-21)
Deliverables:
- Reference entities CRUD (categories/manufacturers/models/classes)
- Assets CRUD + filtering
- Asset state history, transfer, assignment logic
- Passport and class history APIs

Exit Criteria:
- Asset create/update/transfer lifecycle fully testable
- State and assignment history stored correctly

### M3 — Operations Core Complete (Due: 2026-04-28)
Deliverables:
- Warehouse CRUD + parts CRUD
- Stock engine + movement transactions (IN/OUT)
- Repairs flow + repair parts integration
- Expenses module

Exit Criteria:
- Stock cannot become negative
- Repair completion updates cost and related records correctly

### M4 — Governance & Final Integration (Due: 2026-05-05)
Deliverables:
- Request approval pipeline
- Document/signature/file/commission flow
- Audit middleware enabled
- Notifications basic
- Analytics basic endpoints

Exit Criteria:
- Request -> Approval -> Document flow works end-to-end
- Audit logs generated on write operations

### Final Handover (Due: 2026-05-08)
Deliverables:
- Stabilized release candidate
- Regression test report
- Updated docs + runbook
- Known limitations list

Exit Criteria:
- Smoke test checklist 100% pass
- Migration up/down validated

## 4. Weekly Work Plan (Execution Level)

## Week 1: Foundation + Security + Users
- Project bootstrap, environment, logging, exception handling
- Async DB session, migrations
- JWT auth and token lifecycle
- RBAC dependency + role/permission integration
- Users CRUD + pagination + soft delete

## Week 2: Assets Domain
- Reference dictionaries (category/manufacturer/model/class)
- Assets CRUD + filters
- Asset state/lifecycle logic
- Transfer + assignment flow
- Passport APIs

## Week 3: Warehouse + Repairs + Expenses
- Warehouses and parts modules
- Stock and movement transaction engine
- Repairs lifecycle and repair parts
- Expenses linkage (asset/repair)

## Week 4: Integration + Audit + Release
- Request approvals and statuses
- Document signatures and files
- Commission workflow
- Audit + notifications + analytics basic
- Performance tuning + regression + release prep

## 5. Definition of Done (Module-Level)

Each module is DONE only if:
- API endpointlar complete and documented
- Request/response schemas implemented
- Service layer logic separated from routers
- Migration scripts included
- Unit + integration tests added
- RBAC checks applied
- Audit event emitted for write actions
- API spec updated

## 6. Quality Gates and KPI

Technical KPI:
- Unit/integration tests for all P0 flows
- Service-layer coverage target: >= 70%
- Zero blocker/critical defects at release
- Migration reliability: up/down success on clean DB

Operational KPI:
- Milestones delivered on planned date
- No unresolved P0 blockers by week close
- Critical path tasks completed before next milestone

## 7. Risk Register and Mitigation

Risk 1: Schema vs migration mismatch
- Mitigation: migration freeze policy at end of Week 1

Risk 2: Request/Document flow complexity
- Mitigation: isolate and integrate in Week 4 with dedicated buffer

Risk 3: Warehouse/Repair transaction bugs
- Mitigation: atomic transaction tests + negative stock checks

Risk 4: Scope creep in analytics
- Mitigation: strict P0/P1 split, defer advanced analytics

## 8. Reporting Cadence (for Project Manager)

Daily update (short):
- Yesterday done
- Today plan
- Blockers

Weekly report (formal):
- Milestone progress %
- Completed deliverables
- Risks/issues and decision needs
- Next week plan

## 9. Tracking Format

Template:
`[ID] | Module | Task | Owner | ETA(h) | Start | End | Status | Blocker | Note`

Example:
`[W2-04] | Assets | Transfer + Assignment flow | BE-1 | 10h | 2026-04-17 | 2026-04-18 | in_progress | none | history logging done`

## 10. Final Acceptance Checklist (Manager Sign-off)

- P0 scope fully delivered
- Core business flows demo passed
- API documentation complete
- Test report attached
- Deployment runbook attached
- Known limitations approved
- Release tag and changelog prepared
