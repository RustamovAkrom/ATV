# API Audit Summary

**Date:** May 1, 2026
**Audited Components:**
- `src/api/v1/` (all router files)
- `src/schemas/` (all schema files)
- `src/services/` (service return type analysis)

## Key Findings

### 🔴 CRITICAL ISSUES (Must Fix)

#### 1. **17 Endpoints Missing response_model (9 DELETE + 8 POST)**

Endpoints return untyped dict literals without schema validation:

```python
# WRONG - No response_model, untyped response
@router.delete("/{category_id}")
async def delete_category(...):
    return {"status": "deleted"}  # ← FastAPI passes through unvalidated

# RIGHT - response_model enforces schema
@router.delete("/{category_id}", response_model=StatusResponse)
async def delete_category(...):
    return StatusResponse(status="deleted", message=None)
```

**Impact:**
- API clients receive unexpected field names
- OpenAPI docs don't show actual response structure
- No validation of response data

**Affected endpoints:** See full list in [API_AUDIT_REPORT.md](API_AUDIT_REPORT.md)

---

#### 2. **Inconsistent Response Field Names**

Different endpoints use different field names:
- `{"status": "..."}` - used 9 times
- `{"detail": "..."}` - used 1 time (non-standard)
- `{"deleted": count}` - used 1 time (wrong schema)
- `{"count": count}` - used 1 time (no schema)

**Impact:** API is hard to consume consistently

**Example mismatch:**
```python
# Line 40 in auth/sessions.py - uses "detail"
return {"detail": "All sessions revoked"}

# Line 31 in auth/sessions.py - uses "status"
return {"status": "Session revoked"}

# Line 52 in auth/sessions.py - custom format
return {"deleted": deleted}
```

---

### 🟠 HIGH-PRIORITY ISSUES

#### 3. **Pagination Inconsistencies (3 endpoints)**

| Endpoint | Pattern | Issue |
|----------|---------|-------|
| `GET /notifications` | Hardcoded `limit=50, offset=0` | Client cannot control pagination |
| `GET /audit/*` | Uses `PageSchema` | Missing pagination metadata (pages, has_next) |
| `GET /approvals` | Uses `Depends(get_pagination)` wrapper | Inconsistent with other endpoints |

**Impact:** Unpredictable pagination behavior across API

---

#### 4. **Schema Validation Failures**

**UserOutSchema (line 36):**
```python
class UserOutSchema(BaseModel):
    role: str  # ← Will fail if role is NULL in database
```

Should be: `role: str | None`

**Impact:** Validation errors when returning users without roles

---

#### 5. **HTTP Status Code Misuse**

| Endpoint | Current | Expected | Issue |
|----------|---------|----------|-------|
| POST /forgot-password | 200 | 202 or 201 | Password reset is async, wrong status |
| DELETE /{resource} | 200 with body | 204 No Content | DELETE should return 204 or no body |
| POST (creates) | No status code | 201 Created | Creating resources should return 201 |

---

### 🟡 MEDIUM-PRIORITY ISSUES

#### 6. **Manual DateTime Parsing (Error Prone)**

[analytics/assignment_analytics.py](src/api/v1/analytics/assignment_analytics.py#L50)
```python
# Current - manual string parsing
date_from: str | None = Query(None, description="ISO format datetime")
...
date_from_dt = parse_optional_datetime(date_from)  # ← Can fail at runtime

# Better - Pydantic native parsing
date_from: datetime | None = Query(None)
```

**Impact:** Runtime errors if datetime parsing fails; no compile-time validation

---

#### 7. **No Error Response Documentation**

None of the ~50 endpoints document error responses:

```python
# Current - no error docs
@router.get("/users/{user_id}", response_model=UserOutSchema)

# Should have:
@router.get(
    "/users/{user_id}",
    response_model=UserOutSchema,
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
```

**Impact:** OpenAPI docs don't show what error responses look like

---

### 🟢 LOW-PRIORITY ISSUES

#### 8. **ConfigDict Inconsistency**

`StatusResponse` missing `model_config = ConfigDict(from_attributes=True)` while other schemas have it.

**Impact:** Inconsistent ORM integration behavior

---

#### 9. **Service Return Type Ambiguity**

Some services return raw ORM models instead of schemas:
```python
# rbac.py line 31-40
return await service.list_roles()  # ← Returns what type? Raw models or schemas?
```

**Impact:** Type hints unclear; downstream code must handle conversion

---

## Statistics

```
Total Issues: 36
├── CRITICAL:  17 (Missing response_model)
├── HIGH:       4
├── MEDIUM:     9
└── LOW:        6

By Category:
├── Missing response_model:      17 (47%)
├── Response field mismatch:      3 (8%)
├── Pagination:                   3 (8%)
├── Status code:                  2 (6%)
├── Schema validation:            2 (6%)
├── Service types:                2 (6%)
├── Configuration:                1 (3%)
├── DateTime parsing:             1 (3%)
├── Error documentation:          1 (3%)
└── Misc (circular refs, docs):   3 (8%)

Files Most Affected:
├── src/api/v1/auth/           4 issues
├── src/api/v1/users/          6 issues
├── src/api/v1/assets/         9 issues
├── src/api/v1/notifications/  3 issues
└── src/schemas/               2 issues
```

---

## Risk Assessment

### High Risk (Can cause client failures)
1. ❌ Missing response_model on 17 endpoints - clients get unvalidated data
2. ❌ Inconsistent response fields - clients can't parse responses predictably
3. ❌ Invalid HTTP status codes - clients implement wrong retry logic

### Medium Risk (Causes bugs intermittently)
1. ⚠️ Schema validation errors for null roles - breaks when users lack roles
2. ⚠️ Manual datetime parsing - fails on invalid input
3. ⚠️ Hardcoded pagination - clients can't control result size

### Low Risk (Documentation/consistency)
1. ℹ️ Missing error responses in docs - harder to debug
2. ℹ️ Inconsistent ConfigDict - minor ORM integration issues

---

## Fix Effort Estimate

| Phase | Tasks | Effort |
|-------|-------|--------|
| P1: Critical | Add response_model to 17 endpoints | 30 min |
| P1: Critical | Create 3 custom response schemas | 15 min |
| P1: Critical | Fix UserOutSchema | 5 min |
| P2: Important | Add ConfigDict to StatusResponse | 5 min |
| P2: Important | Fix pagination patterns | 30 min |
| P3: Should | Add error response documentation | 1 hour |
| P3: Should | Fix HTTP status codes | 15 min |
| **Total** | | **~2 hours** |

---

## Recommended Implementation Order

### Immediate (Next commit)
1. ✅ Add `response_model=StatusResponse` to all 17 DELETE/POST endpoints
2. ✅ Create 3 custom schemas (CleanupResponse, UnreadCountResponse, etc.)
3. ✅ Fix UserOutSchema nullable fields

### Follow-up (Next PR)
1. ✅ Add ConfigDict to StatusResponse
2. ✅ Standardize pagination (PageOutSchema everywhere)
3. ✅ Add proper HTTP status codes

### Later (Documentation sprint)
1. 📝 Add error response documentation
2. 📝 Add endpoint docstrings
3. 📝 Add inline type hints for service methods

---

## Deliverables

This audit includes:

1. **[API_AUDIT_REPORT.md](API_AUDIT_REPORT.md)** - Detailed findings with line numbers and examples (18 sections)
2. **[API_AUDIT_ISSUES.json](API_AUDIT_ISSUES.json)** - Machine-readable issue list (36 issues) with severity, file, line, and recommended fix
3. **[QUICK_FIX_GUIDE.md](QUICK_FIX_GUIDE.md)** - Step-by-step fix instructions with before/after code
4. **[API_AUDIT_SUMMARY.md](API_AUDIT_SUMMARY.md)** - This document

---

## Next Steps

1. **Review** findings with team
2. **Prioritize** fixes using severity/effort matrix
3. **Implement** critical fixes in current sprint
4. **Test** with automated validation
5. **Update** API development guidelines

---

## Validation Script (Optional)

```bash
#!/bin/bash
# Verify all endpoints have response_model defined

grep -r "@router\." src/api/v1/ | grep -v "response_model" | grep -v "#" | wc -l

# Should output: 0 (all endpoints have response_model)
```

---

## Contact

For questions about these findings, see individual issue details in:
- **Short version:** This file
- **Detailed version:** [API_AUDIT_REPORT.md](API_AUDIT_REPORT.md)
- **Structured data:** [API_AUDIT_ISSUES.json](API_AUDIT_ISSUES.json)
- **How to fix:** [QUICK_FIX_GUIDE.md](QUICK_FIX_GUIDE.md)

