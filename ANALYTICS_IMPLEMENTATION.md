# Analytics Layer Implementation Documentation

## Overview

A production-grade analytics (READ) layer has been implemented following CQRS-lite principles, separating read operations from the existing write layer (WRITE). This layer provides comprehensive analytics, metrics, and dashboards without modifying any existing functionality.

## Architecture

### CQRS-Lite Approach

```
WRITE LAYER (Existing - Unchanged)
├── /api/v1/assets/*         (CREATE, UPDATE, DELETE)
├── /api/v1/approvals        (CREATE, UPDATE)
├── /api/v1/assignments      (CREATE, UPDATE)
└── /api/v1/transfers        (CREATE, UPDATE)

READ LAYER (New Analytics - Separate)
├── /api/v1/analytics/asset-history      (History queries + aggregates)
├── /api/v1/analytics/assignments        (Assignment analytics)
├── /api/v1/analytics/transfers          (Transfer analytics)
└── /api/v1/analytics/dashboard          (Dashboard overview)
```

### Layered Architecture

```
API Layer
  ├── /api/v1/analytics/asset_history.py
  ├── /api/v1/analytics/assignment_analytics.py
  ├── /api/v1/analytics/transfer_analytics.py
  └── /api/v1/analytics/analytics_dashboard.py

Services Layer
  ├── services/analytics/asset_history_analytics_service.py
  ├── services/analytics/asset_assignment_analytics_service.py
  ├── services/analytics/asset_transfer_analytics_service.py
  └── services/analytics/dashboard_analytics_service.py

Repository Layer (Read-Optimized)
  ├── repositories/analytics/asset_history_analytics_repo.py
  ├── repositories/analytics/asset_assignment_analytics_repo.py
  └── repositories/analytics/asset_transfer_analytics_repo.py

Schemas Layer
  ├── schemas/analytics/asset_history.py
  ├── schemas/analytics/asset_assignment_analytics.py
  ├── schemas/analytics/asset_transfer_analytics.py
  └── schemas/analytics/dashboard_metrics.py
```

## Features Implemented

### 1. Asset History Analytics

**Endpoints:**
- `GET /analytics/asset-history/` - List history with filters and pagination
- `GET /analytics/asset-history/aggregates` - Aggregated metrics
- `POST /analytics/asset-history/search` - Complex search

**Capabilities:**
- Filter by asset, user, action, date range, search terms
- Pagination (page, limit, offset)
- Aggregated metrics: unique assets, users, actions breakdown
- Identifies most active asset and user

**Performance:**
- SelectInLoad for asset/user relationships (no N+1)
- Count queries use index-friendly subqueries

### 2. Asset Assignment Analytics

**Endpoints:**
- `GET /analytics/assignments/` - List all assignments
- `GET /analytics/assignments/active` - Active assignments only
- `GET /analytics/assignments/user/{user_id}/summary` - User-specific summary
- `GET /analytics/assignments/asset/{asset_id}/timeline` - Complete assignment timeline
- `GET /analytics/assignments/aggregates` - Aggregated metrics

**Capabilities:**
- Filter by asset, user, status (active/inactive), date range
- Duration calculation for each assignment
- Timeline view showing assignment history for each asset
- User-level metrics: active/total assignments, average duration
- Aggregates: total active, most frequently assigned asset, most active user

**Performance:**
- SelectInLoad for relationships
- Duration calculations avoid N+1
- Efficient distinct counts with func.distinct()

### 3. Asset Transfer Analytics

**Endpoints:**
- `GET /analytics/transfers/` - List all transfers
- `GET /analytics/transfers/pending` - Pending transfers (sorted by age)
- `GET /analytics/transfers/asset/{asset_id}/history` - Asset transfer history
- `GET /analytics/transfers/metrics` - Aggregated metrics
- `GET /analytics/transfers/bottlenecks` - Bottleneck report
- `GET /analytics/transfers/warehouse/{warehouse_id}/metrics` - Warehouse metrics

**Capabilities:**
- Filter by asset, warehouse, service, status, date range, creator
- Transfer history with full location details
- Duration metrics:
  - Pending duration (time waiting for approval)
  - Total completion time (entire transfer duration)
  - Days to completion after approval
- Bottleneck detection:
  - Critical: Pending > 30 days
  - Warning: Pending > 7 days
- Warehouse-level metrics (transfers in/out, pending in/out)

**Performance:**
- SelectInLoad for all related entities
- Efficient date-based filtering for bottleneck detection
- Warehouse metrics use distinct counts

### 4. Dashboard Analytics

**Endpoints:**
- `GET /analytics/dashboard/overview` - Complete dashboard overview

**Metrics Provided:**
- **Assignment Metrics**: active count, inactive count, average duration
- **Transfer Metrics**: pending, completed, average completion time, critical bottlenecks
- **Asset History**: total entries, most active asset/user
- **Quick Stats**:
  - Total assets with active assignments
  - Total users with active assignments
  - Total assets in pending transfers

**Dashboard Structure:**
```json
{
  "timestamp": "ISO datetime",
  "period": "all_time|today|this_week|this_month",
  "assignment_metrics": {
    "total_active": 45,
    "total_inactive": 120,
    "average_duration_days": 12.5
  },
  "transfer_metrics": {
    "total_pending": 8,
    "total_completed": 245,
    "average_completion_days": 2.3,
    "critical_bottlenecks": 2
  },
  "asset_history_metrics": {
    "total_history_entries": 5432,
    "most_active_asset_id": "uuid",
    "most_active_asset_name": "Asset Name",
    "last_history_entry_date": "ISO datetime"
  },
  "total_assets_with_active_assignments": 45,
  "total_users_with_active_assignments": 28,
  "total_assets_in_transfer": 8
}
```

## Performance Optimization

### Query Optimization

1. **SelectInLoad** - Eager loading for common relationships
   ```python
   selectinload(AssetAssignment.asset)
   selectinload(AssetAssignment.user)
   ```

2. **Avoid N+1 Queries**
   - All relationships eager-loaded in first query
   - No separate queries in service layer

3. **Efficient Aggregation**
   - Use SQL `COUNT(DISTINCT ...)` for unique counts
   - `GROUP BY` for breakdown metrics
   - `ORDER BY` for pagination

4. **Index-Friendly Filtering**
   - Filters applied directly in SQL WHERE clause
   - Foreign key joins use existing indexes

### Caching Strategy

All analytics endpoints are cached with TTL (Time-To-Live):

- **List endpoints**: 60 seconds (frequent changes)
- **Active/Pending lists**: 30 seconds (real-time)
- **User/Asset details**: 300 seconds (less frequent)
- **Aggregates/Metrics**: 600 seconds (stable data)
- **Dashboard**: 300 seconds (balanced freshness)

**Cache Tags:**
- `analytics:asset-history:*`
- `analytics:assignments:*`
- `analytics:transfers:*`
- `analytics:dashboard:*`

Cache invalidation happens when:
- Related assets are modified (via existing cache invalidation)
- Assignments created/updated
- Transfers status changes

## Security & RBAC

All analytics endpoints are protected with:

```python
@router.get(..., dependencies=[presets.CanViewAssets])
```

This ensures:
- User must be authenticated
- User must have `ASSETS_VIEW` permission
- No additional permission required (reads don't modify data)
- Maintains separation between write (ASSETS_CREATE/UPDATE/DELETE) and read (ASSETS_VIEW)

### Permission Mapping

```
SUPERADMIN:  ✓ All access
ADMIN:       ✓ All access + ASSETS_VIEW
MODERATOR:   ✓ ASSETS_VIEW
ANALYTIC:    ✓ ASSETS_VIEW + AUDIT_VIEW
USER:        ✗ No analytics access
```

## Response Design

All responses are optimized for dashboards and charts:

### Asset Assignment Response
```json
{
  "id": "uuid",
  "asset_id": "uuid",
  "asset_name": "Asset Name",
  "asset_tag": "TAG-001",
  "user_id": "uuid",
  "user_name": "User Name",
  "user_email": "user@example.com",
  "assigned_at": "ISO datetime",
  "unassigned_at": "ISO datetime or null",
  "status": "active|inactive",
  "duration_metrics": {
    "duration_days": 12.5,
    "duration_formatted": "12 days, 12 hours",
    "is_active": true
  }
}
```

### Transfer Response
```json
{
  "id": "uuid",
  "asset_id": "uuid",
  "asset_name": "Asset Name",
  "status": "pending|completed|cancelled",
  "from_warehouse_name": "Warehouse 1",
  "to_warehouse_name": "Warehouse 2",
  "created_by_name": "User Name",
  "created_at": "ISO datetime",
  "transferred_at": "ISO datetime or null",
  "duration_metrics": {
    "pending_duration_days": 5,
    "pending_duration_formatted": "5 days, 3 hours",
    "total_duration_days": 6,
    "is_pending": false
  }
}
```

## Filtering System

### Asset History Filters
- `asset_id` - Specific asset
- `user_id` - Specific user
- `action` - Specific action type
- `date_from` - Start of date range (ISO format)
- `date_to` - End of date range (ISO format)
- `search` - Full-text search (asset name/tag or user name)

### Assignment Filters
- `asset_id` - Specific asset
- `user_id` - Specific user
- `status` - "active" or "inactive"
- `date_from` / `date_to` - Date range
- `search` - Asset name/tag or user name

### Transfer Filters
- `asset_id` - Specific asset
- `created_by_id` - Created by user
- `received_by_id` - Received by user
- `from_warehouse_id` - Source warehouse
- `to_warehouse_id` - Destination warehouse
- `from_service_id` - Source service
- `to_service_id` - Destination service
- `status` - "pending", "completed", or "cancelled"
- `date_from` / `date_to` - Date range
- `search` - Asset name/tag

## Pagination

Standard pagination used across all list endpoints:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "limit": 20
}
```

Query parameters:
- `page` - Page number (default: 1, minimum: 1)
- `limit` - Items per page (default: 20, minimum: 1, maximum: 100)

Calculated offset: `(page - 1) * limit`

## Data Integrity

1. **No Sensitive Data Exposed**
   - User emails included for contact purposes
   - No passwords or tokens
   - No internal IDs leaked

2. **Input Validation**
   - All filters validated with Pydantic schemas
   - Date formats validated (ISO 8601)
   - Enum values validated (status, actions)

3. **Query Safety**
   - Parameterized queries (SQLAlchemy ORM)
   - No string concatenation in SQL
   - No SQL injection possible

## Future Extensions

### Optional: Background Tasks for Heavy Analytics

If analytics queries become too heavy, implement async report generation:

```python
# tasks/analytics_tasks.py
@celery_app.task
async def generate_transfer_report(date_from, date_to):
    """Generate comprehensive transfer report as background task."""
    # Query data
    # Format report (CSV, PDF)
    # Store in S3/local storage
    # Return download link
    pass
```

### Optional: Advanced Caching

Implement Redis caching with cache-aside pattern:

```python
# core/cache/analytics_cache.py
class AnalyticsCache:
    async def get_or_compute_metrics(key, compute_fn, ttl=600):
        """Get from cache or compute and store."""
        value = await redis.get(key)
        if value:
            return json.loads(value)

        value = await compute_fn()
        await redis.setex(key, ttl, json.dumps(value))
        return value
```

### Optional: Advanced Aggregations

Time-series aggregations for trends:

```python
# GET /analytics/assignments/trends?period=daily&from=2024-01-01&to=2024-12-31
# Returns daily breakdown of assignment metrics
```

## Files Added/Modified

### New Files Created
```
src/schemas/analytics/
  ├── asset_assignment_analytics.py (NEW)
  ├── asset_transfer_analytics.py (NEW)
  ├── dashboard_metrics.py (NEW)
  └── asset_history.py (ENHANCED)

src/repositories/analytics/
  ├── asset_assignment_analytics_repo.py (NEW)
  ├── asset_transfer_analytics_repo.py (NEW)
  └── asset_history_analytics_repo.py (ENHANCED)

src/services/analytics/
  ├── asset_assignment_analytics_service.py (NEW)
  ├── asset_transfer_analytics_service.py (NEW)
  ├── dashboard_analytics_service.py (NEW)
  └── asset_history_analytics_service.py (ENHANCED)

src/api/v1/analytics/
  ├── assignment_analytics.py (NEW)
  ├── transfer_analytics.py (NEW)
  └── analytics_dashboard.py (NEW)
  └── asset_history.py (ENHANCED)

src/api/dependencies/
  └── analytics.py (ENHANCED)
```

### Modified Files
```
src/api/router.py
  - Added imports for new analytics routers
  - Included new analytics routers in main router
  - No existing functionality modified
```

### No Breaking Changes
- All existing endpoints unchanged
- All existing models unchanged
- All existing services unchanged
- All existing APIs unchanged
- Backward compatible 100%

## Testing Recommendations

### Unit Tests
```python
# tests/test_analytics_repos.py
async def test_asset_assignment_list_filters():
    # Test each filter individually
    # Test combinations of filters
    # Verify pagination correctness
    # Verify N+1 query prevention

# tests/test_analytics_services.py
async def test_assignment_duration_calculation():
    # Test duration in different scenarios
    # Test active vs inactive status

# tests/test_analytics_apis.py
@pytest.mark.asyncio
async def test_get_assignment_aggregates():
    # Test endpoint response structure
    # Test with various filter combinations
```

### Integration Tests
```python
# tests/test_analytics_integration.py
async def test_dashboard_overview_consistency():
    # Verify dashboard metrics match individual endpoints
    # Verify counts add up correctly

async def test_bottleneck_detection():
    # Create pending transfer
    # Wait/mock time passage
    # Verify bottleneck detection
```

### Performance Tests
```python
# tests/test_analytics_performance.py
async def test_list_assignments_no_n_plus_1():
    # Query with profiler
    # Verify single query per entity type

async def test_cache_effectiveness():
    # Call endpoint twice
    # Verify second call uses cache
```

## Monitoring & Alerting

### Recommended Metrics
- Analytics endpoint response times (should be < 500ms with cache)
- Cache hit/miss ratio
- Database query time breakdown
- Transfer bottleneck count (alert if > threshold)
- Assignment churn rate

### Health Check
```python
# GET /analytics/health
{
  "status": "healthy",
  "cache": "connected",
  "database": "responding",
  "response_time_ms": 45
}
```

## Deployment Notes

1. **No Database Migrations Required**
   - Uses existing models
   - No schema changes
   - No new tables

2. **No New Dependencies**
   - Uses existing FastAPI, SQLAlchemy, Redis
   - No new packages required

3. **Cache Warmup** (Optional)
   - Pre-compute common aggregates on startup
   - Load dashboard metrics into cache

4. **Monitoring Setup**
   - Configure slow query alerts (> 1000ms)
   - Monitor cache hit rates
   - Alert on bottleneck count increase

## Support & Maintenance

### Adding New Analytics Feature
1. Create new schema in `schemas/analytics/`
2. Create new repository in `repositories/analytics/`
3. Create new service in `services/analytics/`
4. Create new endpoint in `api/v1/analytics/`
5. Update `api/dependencies/analytics.py`
6. Update `api/router.py` to include new router

### Troubleshooting

**Query too slow?**
- Check cache is working
- Verify selectinload is used for relationships
- Add indexes to frequently filtered columns

**Memory high?**
- Reduce cache TTL
- Implement pagination limits

**Stale data?**
- Reduce cache TTL
- Add cache invalidation triggers
