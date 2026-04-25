# Analytics API Quick Reference

## Base URL
All endpoints are prefixed with: `/api/v1`

## Authentication
All endpoints require valid JWT token in Authorization header:
```
Authorization: Bearer <token>
```

## Permissions
All analytics endpoints require: `ASSETS_VIEW` permission

---

## Asset History Analytics

### List Asset History
```
GET /analytics/asset-history/
```

**Query Parameters:**
- `asset_id` (UUID, optional) - Filter by asset
- `user_id` (UUID, optional) - Filter by user
- `action` (string, optional) - Filter by action type
- `date_from` (ISO datetime, optional) - Start date
- `date_to` (ISO datetime, optional) - End date
- `search` (string, optional) - Search by asset name/tag or user name
- `page` (integer, optional, default: 1) - Page number
- `limit` (integer, optional, default: 20, max: 100) - Items per page

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "asset_id": "uuid",
      "asset_name": "Asset Name",
      "user_id": "uuid",
      "user_name": "User Name",
      "action": "status_change",
      "description": "Status changed to ACTIVE",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1250,
  "page": 1,
  "limit": 20
}
```

### Get Asset History Aggregates
```
GET /analytics/asset-history/aggregates
```

**Query Parameters:**
- Same as above (all optional for filtering)

**Response:**
```json
{
  "total_entries": 5432,
  "unique_assets": 120,
  "unique_users": 45,
  "date_range_start": "2023-01-01T00:00:00Z",
  "date_range_end": "2024-01-15T10:30:00Z",
  "actions_breakdown": [
    {
      "action": "status_change",
      "count": 2345,
      "last_occurrence": "2024-01-15T10:30:00Z",
      "first_occurrence": "2023-01-01T00:00:00Z"
    }
  ],
  "most_active_asset_id": "uuid",
  "most_active_asset_name": "Critical Asset",
  "most_active_user_id": "uuid",
  "most_active_user_name": "John Doe"
}
```

### Search Asset History
```
POST /analytics/asset-history/search
```

**Body:**
```json
{
  "asset_id": null,
  "user_id": null,
  "action": "status_change",
  "date_from": "2024-01-01T00:00:00Z",
  "date_to": "2024-01-31T23:59:59Z",
  "search": "Critical"
}
```

**Query Parameters:**
- `page` (integer, optional, default: 1)
- `limit` (integer, optional, default: 20)

---

## Asset Assignment Analytics

### List All Assignments
```
GET /analytics/assignments/
```

**Query Parameters:**
- `asset_id` (UUID, optional)
- `user_id` (UUID, optional)
- `status` (string, optional) - "active" or "inactive"
- `date_from` (ISO datetime, optional)
- `date_to` (ISO datetime, optional)
- `search` (string, optional)
- `page` (integer, optional, default: 1)
- `limit` (integer, optional, default: 20)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "asset_id": "uuid",
      "asset_name": "Laptop",
      "asset_tag": "LAP-001",
      "user_id": "uuid",
      "user_name": "John Doe",
      "user_email": "john@example.com",
      "assigned_at": "2024-01-01T09:00:00Z",
      "unassigned_at": null,
      "status": "active"
    }
  ],
  "total": 156,
  "page": 1,
  "limit": 20
}
```

### List Active Assignments
```
GET /analytics/assignments/active
```

**Query Parameters:**
- `page` (integer, optional, default: 1)
- `limit` (integer, optional, default: 20)

### Get User Assignment Summary
```
GET /analytics/assignments/user/{user_id}/summary
```

**Response:**
```json
{
  "user_id": "uuid",
  "user_name": "John Doe",
  "user_email": "john@example.com",
  "active_assignments_count": 3,
  "total_assignments_count": 45,
  "average_duration_days": 12.5,
  "longest_assignment_days": 180,
  "recent_assignment_date": "2024-01-15T10:30:00Z"
}
```

### Get Asset Assignment Timeline
```
GET /analytics/assignments/asset/{asset_id}/timeline
```

**Response:**
```json
{
  "asset_id": "uuid",
  "asset_name": "Laptop",
  "total_assignments": 5,
  "active_assignment": {
    "id": "uuid",
    "asset_id": "uuid",
    "asset_name": "Laptop",
    "asset_tag": "LAP-001",
    "user_id": "uuid",
    "user_name": "John Doe",
    "user_email": "john@example.com",
    "assigned_at": "2024-01-01T09:00:00Z",
    "unassigned_at": null,
    "status": "active"
  },
  "timeline": [
    {
      "sequence": 1,
      "assigned_at": "2023-01-01T09:00:00Z",
      "unassigned_at": "2023-03-15T17:00:00Z",
      "user_id": "uuid",
      "user_name": "Alice Smith",
      "duration_days": 73
    }
  ]
}
```

### Get Assignment Aggregates
```
GET /analytics/assignments/aggregates
```

**Query Parameters:** (all optional for filtering)
- `asset_id`, `user_id`, `status`, `date_from`, `date_to`

**Response:**
```json
{
  "total_active_assignments": 156,
  "total_inactive_assignments": 2341,
  "total_assignments": 2497,
  "average_assignment_duration_days": 15.3,
  "longest_assignment_duration_days": 730,
  "most_frequently_assigned_asset_id": "uuid",
  "most_frequently_assigned_asset_name": "Laptop Model X",
  "most_active_user_id": "uuid",
  "most_active_user_name": "John Doe"
}
```

---

## Asset Transfer Analytics

### List All Transfers
```
GET /analytics/transfers/
```

**Query Parameters:**
- `asset_id` (UUID, optional)
- `created_by_id` (UUID, optional)
- `received_by_id` (UUID, optional)
- `from_warehouse_id` (UUID, optional)
- `to_warehouse_id` (UUID, optional)
- `from_service_id` (UUID, optional)
- `to_service_id` (UUID, optional)
- `status` (string, optional) - "pending", "completed", or "cancelled"
- `date_from` (ISO datetime, optional)
- `date_to` (ISO datetime, optional)
- `search` (string, optional)
- `page` (integer, optional, default: 1)
- `limit` (integer, optional, default: 20)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "asset_id": "uuid",
      "asset_name": "Printer",
      "asset_tag": "PRT-001",
      "status": "completed",
      "from_warehouse_name": "Main Warehouse",
      "to_warehouse_name": "Branch Office",
      "from_service_name": null,
      "to_service_name": null,
      "created_by_id": "uuid",
      "created_by_name": "Admin User",
      "created_at": "2024-01-10T09:00:00Z",
      "received_by_id": "uuid",
      "received_by_name": "Branch Manager",
      "transferred_at": "2024-01-12T14:30:00Z",
      "comment": "Arrived in good condition"
    }
  ],
  "total": 450,
  "page": 1,
  "limit": 20
}
```

### List Pending Transfers
```
GET /analytics/transfers/pending
```

**Query Parameters:**
- `page` (integer, optional, default: 1)
- `limit` (integer, optional, default: 20)

**Note:** Returns pending transfers sorted by creation date (oldest first)

### Get Asset Transfer History
```
GET /analytics/transfers/asset/{asset_id}/history
```

**Response:**
```json
{
  "asset_id": "uuid",
  "asset_name": "Printer",
  "total_transfers": 3,
  "completed_transfers": 2,
  "pending_transfers": 0,
  "cancelled_transfers": 1,
  "history": [
    {
      "transfer_id": "uuid",
      "sequence": 1,
      "status": "completed",
      "from_location": "Main Warehouse",
      "to_location": "Branch Office",
      "created_at": "2024-01-10T09:00:00Z",
      "transferred_at": "2024-01-12T14:30:00Z",
      "created_by_name": "Admin User",
      "duration_days": 2
    }
  ]
}
```

### Get Transfer Metrics
```
GET /analytics/transfers/metrics
```

**Query Parameters:** (all optional for filtering)
- `asset_id`, `created_by_id`, `status`, `date_from`, `date_to`

**Response:**
```json
{
  "total_transfers": 450,
  "completed_transfers": 420,
  "pending_transfers": 25,
  "cancelled_transfers": 5,
  "average_completion_time_days": 2.5,
  "longest_completion_time_days": 15,
  "shortest_completion_time_days": 0,
  "oldest_pending_transfer_days": 8,
  "oldest_pending_transfer_id": "uuid",
  "transfers_pending_over_7_days": 5,
  "transfers_pending_over_30_days": 0,
  "status_breakdown": [
    {
      "status": "completed",
      "count": 420,
      "percentage": 93.33,
      "average_pending_days": null
    },
    {
      "status": "pending",
      "count": 25,
      "percentage": 5.56,
      "average_pending_days": 0
    },
    {
      "status": "cancelled",
      "count": 5,
      "percentage": 1.11,
      "average_pending_days": null
    }
  ]
}
```

### Get Transfer Bottlenecks
```
GET /analytics/transfers/bottlenecks
```

**Query Parameters:**
- `critical_days` (integer, optional, default: 30) - Defines critical threshold
- `warning_days` (integer, optional, default: 7) - Defines warning threshold

**Response:**
```json
{
  "total_bottlenecks": 7,
  "critical_bottlenecks": [
    {
      "transfer_id": "uuid",
      "asset_name": "Server",
      "asset_tag": "SRV-001",
      "status": "pending",
      "pending_days": 45,
      "created_by_name": "Admin User",
      "from_location": "Old Datacenter",
      "to_location": "New Datacenter",
      "created_at": "2023-12-01T09:00:00Z"
    }
  ],
  "warning_bottlenecks": [
    {
      "transfer_id": "uuid",
      "asset_name": "Printer",
      "asset_tag": "PRT-001",
      "status": "pending",
      "pending_days": 12,
      "created_by_name": "Admin User",
      "from_location": "Main Office",
      "to_location": "Branch Office",
      "created_at": "2024-01-03T09:00:00Z"
    }
  ]
}
```

### Get Warehouse Transfer Metrics
```
GET /analytics/transfers/warehouse/{warehouse_id}/metrics
```

**Response:**
```json
{
  "warehouse_id": "uuid",
  "warehouse_name": "Main Warehouse",
  "transfers_from": 245,
  "transfers_to": 198,
  "pending_in": 5,
  "pending_out": 8,
  "average_duration_days": 2.3
}
```

---

## Dashboard Analytics

### Get Dashboard Overview
```
GET /analytics/dashboard/overview
```

**Query Parameters:**
- `period` (string, optional, default: "all_time") - "all_time", "today", "this_week", "this_month"

**Response:**
```json
{
  "timestamp": "2024-01-15T15:45:30Z",
  "period": "all_time",
  "assignment_metrics": {
    "total_active": 156,
    "total_inactive": 2341,
    "average_duration_days": 15.3
  },
  "transfer_metrics": {
    "total_pending": 25,
    "total_completed": 420,
    "average_completion_days": 2.5,
    "critical_bottlenecks": 2
  },
  "asset_history_metrics": {
    "total_history_entries": 54321,
    "most_active_asset_id": "uuid",
    "most_active_asset_name": "Critical Server",
    "last_history_entry_date": "2024-01-15T14:30:00Z"
  },
  "total_assets_with_active_assignments": 156,
  "total_users_with_active_assignments": 45,
  "total_assets_in_transfer": 25
}
```

---

## Error Responses

All endpoints follow standard error format:

```json
{
  "detail": "Error message describing what went wrong",
  "status": 400
}
```

### Common Error Codes

- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

---

## Caching

All endpoints are cached with the following TTLs:

- List endpoints: 60 seconds
- Active/Pending lists: 30 seconds
- User/Asset timelines: 300 seconds
- Aggregates/Metrics: 600 seconds
- Dashboard: 300 seconds

Add `?nocache=true` to any request to bypass cache (if enabled in config).

---

## Date Format

All datetime parameters and responses use ISO 8601 format:
```
YYYY-MM-DDTHH:MM:SSZ
Example: 2024-01-15T10:30:00Z
```

---

## Pagination

List endpoints support standard pagination:

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `limit` (integer, default: 20, max: 100) - Items per page

**Response Structure:**
```json
{
  "items": [...],
  "total": 1500,
  "page": 1,
  "limit": 20
}
```

Calculate total pages: `Math.ceil(total / limit)`

---

## Examples

### Example 1: Get Active Assignments for Specific User
```bash
curl -X GET "http://api.example.com/api/v1/analytics/assignments/user/550e8400-e29b-41d4-a716-446655440000/summary" \
  -H "Authorization: Bearer eyJhbGci..."
```

### Example 2: Find Transfer Bottlenecks
```bash
curl -X GET "http://api.example.com/api/v1/analytics/transfers/bottlenecks?critical_days=30&warning_days=7" \
  -H "Authorization: Bearer eyJhbGci..."
```

### Example 3: Dashboard Data for Frontend
```bash
curl -X GET "http://api.example.com/api/v1/analytics/dashboard/overview?period=this_month" \
  -H "Authorization: Bearer eyJhbGci..."
```

### Example 4: Asset History with Filters
```bash
curl -X GET "http://api.example.com/api/v1/analytics/asset-history/?asset_id=550e8400-e29b-41d4-a716-446655440000&date_from=2024-01-01T00:00:00Z&page=1&limit=50" \
  -H "Authorization: Bearer eyJhbGci..."
```
