# Analytics API

All endpoints require `Authorization: Bearer <token>` and the asset view
permission currently enforced by `AssetPermissions.CanViewAssets`.

## Frontend Endpoint Catalog

### GET /api/v1/analytics/dashboard/overview/
**Description**: Returns all-time KPI blocks for the dashboard: assignment totals,
transfer totals, and asset history totals.
**Query params**: none.
**Response**:
```json
{
  "period": "all_time",
  "assignment_metrics": {"total_active": 8, "total_inactive": 4, "total_assignments": 12},
  "transfer_metrics": {"total_pending": 2, "total_transfers": 10},
  "asset_history_metrics": {"total_history_entries": 80, "unique_assets": 30, "unique_users": 12}
}
```
**Frontend use**: Main analytics dashboard KPI widgets.

### GET /api/v1/analytics/assets/overview
**Description**: Returns a combined asset overview report with KPIs from asset,
repair, transfer, approval, document, and utilization analytics.
**Query params**: `region_id`, `service_id`, `date_from`, `date_to`.
**Response**:
```json
{
  "data": {"kpis": [{"key": "assets_total", "label": "Assets", "value": 1250}]},
  "meta": {"generated_at": "2026-05-27T12:00:00Z", "filters": {"region_id": null, "service_id": null, "date_from": null, "date_to": null}}
}
```
**Frontend use**: Executive dashboard and overview page.

### GET /api/v1/analytics/assets/distribution
**Description**: Returns asset distribution grouped by business dimensions such as
status, region, service, or category depending on repository data.
**Query params**: `region_id`, `service_id`, `date_from`, `date_to`.
**Response**:
```json
{
  "data": {"labels": ["active", "in_repair"], "values": [100, 5], "items": []},
  "meta": {"generated_at": "2026-05-27T12:00:00Z", "filters": {"region_id": null, "service_id": null, "date_from": null, "date_to": null}}
}
```
**Frontend use**: Pie charts, stacked bars, distribution widgets.

### GET /api/v1/analytics/assets/lifecycle
**Description**: Returns lifecycle metrics for assets across creation, assignment,
repair, transfer, and retirement states.
**Query params**: `region_id`, `service_id`, `date_from`, `date_to`.
**Response**:
```json
{
  "data": {"labels": ["created", "assigned", "repaired"], "values": [30, 18, 4]},
  "meta": {"generated_at": "2026-05-27T12:00:00Z", "filters": {"region_id": null, "service_id": null, "date_from": null, "date_to": null}}
}
```
**Frontend use**: Asset lifecycle chart.

### GET /api/v1/analytics/assignments/
**Description**: Lists asset assignments with duration metrics and optional filters.
**Query params**: `asset_id`, `user_id`, `status=active|inactive`,
`date_from`, `date_to`, `search`, `page`, `limit`.
**Response**:
```json
{
  "items": [{"asset_name": "Printer A", "user_name": "Admin", "status": "active", "duration_metrics": {"duration_days": 3, "duration_formatted": "3d 0h", "is_active": true}}],
  "total": 1,
  "page": 1,
  "limit": 20
}
```
**Frontend use**: Assignment table.

### GET /api/v1/analytics/assignments/active
**Description**: Lists currently active assignments.
**Query params**: `page`, `limit`.
**Response**: Same pagination shape as `/analytics/assignments/`.
**Frontend use**: Active assignment widget and operational table.

### GET /api/v1/analytics/assignments/user/{user_id}/summary
**Description**: Returns assignment totals and duration stats for one user.
**Path params**: `user_id`.
**Response**:
```json
{
  "user_id": "00000000-0000-0000-0000-000000000000",
  "user_name": "Admin",
  "user_email": "admin@example.com",
  "active_assignments_count": 3,
  "total_assignments_count": 12,
  "average_duration_days": 5.5,
  "longest_assignment_days": 20,
  "recent_assignment_date": "2026-05-20T10:00:00Z"
}
```
**Frontend use**: User profile analytics panel.

### GET /api/v1/analytics/assignments/asset/{asset_id}/timeline
**Description**: Returns assignment history for one asset in chronological order.
**Path params**: `asset_id`.
**Response**:
```json
{"asset_id": "uuid", "asset_name": "Printer A", "total_assignments": 2, "active_assignment": null, "timeline": []}
```
**Frontend use**: Asset detail timeline.

### GET /api/v1/analytics/assignments/aggregates
**Description**: Returns assignment totals, active/inactive split, and top asset/user.
**Query params**: `asset_id`, `user_id`, `status`, `date_from`, `date_to`.
**Response**:
```json
{"total_active_assignments": 8, "total_inactive_assignments": 4, "total_assignments": 12, "average_assignment_duration_days": 6.2, "longest_assignment_duration_days": 30, "most_frequently_assigned_asset_id": "uuid", "most_frequently_assigned_asset_name": "Laptop", "most_active_user_id": "uuid", "most_active_user_name": "Admin"}
```
**Frontend use**: Assignment KPI cards.

### GET /api/v1/analytics/transfers/
**Description**: Lists asset transfer requests with source/destination details.
**Query params**: `asset_id`, `created_by_id`, `received_by_id`,
`from_warehouse_id`, `to_warehouse_id`, `from_service_id`, `to_service_id`,
`status=pending|completed|cancelled`, `date_from`, `date_to`, `search`, `page`, `limit`.
**Response**: Paginated list of transfer records.
**Frontend use**: Transfer analytics table.

### GET /api/v1/analytics/transfers/pending
**Description**: Lists pending transfers ordered oldest first.
**Query params**: `page`, `limit`.
**Response**: Paginated transfer records.
**Frontend use**: Pending transfer queue.

### GET /api/v1/analytics/transfers/asset/{asset_id}/history
**Description**: Returns transfer history for one asset.
**Path params**: `asset_id`.
**Response**:
```json
{"asset_id": "uuid", "asset_name": "Laptop", "total_transfers": 3, "completed_transfers": 2, "pending_transfers": 1, "cancelled_transfers": 0, "history": []}
```
**Frontend use**: Asset detail movement timeline.

### GET /api/v1/analytics/transfers/metrics
**Description**: Returns transfer counts, completion times, bottleneck indicators,
and status breakdown.
**Query params**: `asset_id`, `created_by_id`, `status`, `date_from`, `date_to`.
**Response**:
```json
{"total_transfers": 10, "completed_transfers": 7, "pending_transfers": 2, "cancelled_transfers": 1, "average_completion_time_days": 2.4, "longest_completion_time_days": 8, "shortest_completion_time_days": 1, "oldest_pending_transfer_days": 9, "oldest_pending_transfer_id": "uuid", "transfers_pending_over_7_days": 1, "transfers_pending_over_30_days": 0, "status_breakdown": []}
```
**Frontend use**: Transfer KPI cards and status charts.

### GET /api/v1/analytics/transfers/bottlenecks
**Description**: Returns warning and critical pending transfer bottlenecks.
**Query params**: `critical_days` default `30`, `warning_days` default `7`.
**Response**:
```json
{"total_bottlenecks": 2, "critical_bottlenecks": [], "warning_bottlenecks": []}
```
**Frontend use**: Alerts table and logistics health widget.

### GET /api/v1/analytics/transfers/warehouse/{warehouse_id}/metrics
**Description**: Returns incoming/outgoing transfer metrics for one warehouse.
**Path params**: `warehouse_id`.
**Response**:
```json
{"warehouse_id": "uuid", "warehouse_name": "Main WH", "transfers_from": 6, "transfers_to": 9, "pending_in": 1, "pending_out": 2, "average_duration_days": 1.5}
```
**Frontend use**: Warehouse detail analytics tab.

### GET /api/v1/analytics/asset-history/
**Description**: Lists asset history events with optional search and filters.
**Query params**: `asset_id`, `user_id`, `action`, `date_from`, `date_to`,
`search`, `page`, `limit`.
**Response**: Paginated history entries.
**Frontend use**: Audit/history table.

### GET /api/v1/analytics/asset-history/aggregates
**Description**: Returns counts of history entries, unique assets/users, action
breakdown, and most active entities.
**Query params**: `asset_id`, `user_id`, `action`, `date_from`, `date_to`.
**Response**:
```json
{"total_entries": 80, "unique_assets": 30, "unique_users": 12, "date_range_start": null, "date_range_end": null, "actions_breakdown": [], "most_active_asset_id": null, "most_active_asset_name": null, "most_active_user_id": null, "most_active_user_name": null}
```
**Frontend use**: History KPI cards and action charts.

### GET /api/v1/analytics/costs/repairs
**Description**: Lists repair labor/parts/total costs.
**Query params**: `page`, `limit`.
**Response**: Paginated repair cost rows.
**Frontend use**: Repair cost report.

### GET /api/v1/analytics/costs/assets
**Description**: Lists asset purchase cost, repair cost, and total cost.
**Query params**: `page`, `limit`.
**Response**: Paginated asset cost rows.
**Frontend use**: Asset total cost of ownership report.

### GET /api/v1/analytics/costs/regions
**Description**: Lists purchase/repair/total costs grouped by region.
**Query params**: `page`, `limit`.
**Response**: Paginated region cost rows.
**Frontend use**: Regional finance dashboard.

### GET /api/v1/analytics/regions/overview
**Description**: Returns region overview data including GeoJSON and asset counts.
**Query params**: none.
**Response**: List of region overview objects.
**Frontend use**: Regional map and summary table.

### GET /api/v1/analytics/regions/{region_id}/details
**Description**: Returns service breakdown and top cost assets for one region.
**Path params**: `region_id`.
**Response**: Region detail object or `null`.
**Frontend use**: Region drill-down page.

### GET /api/v1/analytics/regions/heatmap
**Description**: Returns scored region points for map heat visualization.
**Query params**: none.
**Response**: List of heatmap points.
**Frontend use**: Map heat layer.

### GET /api/v1/analytics/top/assets
**Description**: Returns top assets sorted by selected metric.
**Query params**: `metric=assignments|transfers|repairs`, `limit`.
**Response**: List of top asset rows.
**Frontend use**: Leaderboard widget.

### GET /api/v1/analytics/top/users
**Description**: Returns top users sorted by selected metric. Email is hidden for
non-admin viewers.
**Query params**: `metric=assignments|transfers|repairs`, `limit`.
**Response**: List of top user rows.
**Frontend use**: Operational workload leaderboard.

### GET /api/v1/analytics/top/services
**Description**: Returns top services sorted by selected metric.
**Query params**: `metric=assignments|transfers|repairs`, `limit`.
**Response**: List of top service rows.
**Frontend use**: Service comparison widget.

### GET /api/v1/analytics/trends/assignments
**Description**: Returns assignment counts by time bucket.
**Query params**: `interval=daily|weekly|monthly`, `periods` from 1 to 180.
**Response**: Trend series with bucket start/end and value.
**Frontend use**: Assignment trend line chart.

### GET /api/v1/analytics/trends/transfers
**Description**: Returns transfer counts by time bucket.
**Query params**: `interval=daily|weekly|monthly`, `periods`.
**Response**: Trend series.
**Frontend use**: Transfer trend chart.

### GET /api/v1/analytics/trends/repairs
**Description**: Returns repair counts and total repair cost by time bucket.
**Query params**: `interval=daily|weekly|monthly`, `periods`.
**Response**: Repair trend series.
**Frontend use**: Repair trend and cost chart.

### GET /api/v1/analytics/forecast/repairs
**Description**: Returns deterministic moving-average forecast for repair volume.
**Query params**: `interval=daily|weekly|monthly`, `periods`, `basis_window`.
**Response**:
```json
{"interval": "weekly", "basis_window": 4, "forecast_periods": 8, "moving_average": 2.5, "points": [{"period_index": 1, "forecast_value": 2.5}]}
```
**Frontend use**: Forecast chart.

### GET /api/v1/analytics/forecast/failures
**Description**: Returns moving-average forecast for failures based on repair trend
data.
**Query params**: `interval`, `periods`, `basis_window`.
**Response**: Same shape as repair forecast.
**Frontend use**: Maintenance planning chart.

### GET /api/v1/analytics/alerts/
**Description**: Returns analytics alerts for stuck transfers, excessive repairs,
inactive assets, and overloaded users.
**Query params**: `transfer_days`, `repair_days`, `repair_threshold`,
`inactive_days`, `assignment_threshold`.
**Response**:
```json
[{"alert_type": "stuck_transfer", "severity": "critical", "entity_id": "uuid", "entity_name": "Asset A", "message": "Transfer pending longer than 7 days", "metric_value": 9, "threshold": 7, "detected_at": "2026-05-27T12:00:00Z"}]
```
**Frontend use**: Alert center and dashboard warning panel.

## Architecture

```text
API routers
  -> FastAPI dependencies
    -> specialized services
      -> specialized repositories
        -> SQLAlchemy models

BaseAnalyticsService
  -> validation, privacy filtering, DTO helper methods

BaseAnalyticsRepository
  -> scope filters, date filters, counts, pagination

DashboardAnalyticsService
  -> AssetAssignmentAnalyticsService
  -> AssetTransferAnalyticsService
  -> AssetHistoryAnalyticsService

CostAnalyticsService, TrendAnalyticsService, AlertAnalyticsService,
RegionAnalyticsService, TopAnalyticsService, ForecastAnalyticsService,
ExportAnalyticsService
  -> each owns one analytics concern

interfaces.py
  -> IAggregatable, IDateFilterable, IRegionFilterable, IExportable, ICacheable
```

## Frontend Migration Notes

No endpoint path or response contract was intentionally changed. The dashboard
overview implementation moved from router code into `DashboardAnalyticsService`.
Search normalization moved from `api.v1.analytics._utils` to
`utils.analytics.filter_utils`; the old import path remains available for
compatibility.
