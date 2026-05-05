(IIB ATV) PS E:\IIB ATV> task test-cov
task: [test-setup] docker compose down -v postgres-test || true
[+] down 2/2
 ✔ Container iibatv-postgres-test-1 Removed                                                                                   0.5s
 ! Network iibatv_backend_network   Resource is still in use                                                                  0.0s
task: [test-setup] docker compose up -d --wait postgres-test
[+] up 1/1
 ✔ Container iibatv-postgres-test-1 Healthy                                                                                   6.0s
task: [test-cov] uv run --no-sync coverage run -m pytest -vv
====================================================== test session starts ======================================================
platform win32 -- Python 3.12.0, pytest-9.0.3, pluggy-1.6.0 -- E:\IIB ATV\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: E:\IIB ATV
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.13.0
collected 119 items

tests/api/analytics/test_analytics_api.py::test_dashboard_overview_returns_stable_payload PASSED                           [  0%]
tests/api/analytics/test_analytics_api.py::test_regions_endpoints_return_geo_and_aggregates PASSED                         [  1%]
tests/api/analytics/test_analytics_api.py::test_assignment_analytics_filters_aggregates_and_timeline PASSED                [  2%]
tests/api/analytics/test_analytics_api.py::test_transfer_analytics_list_metrics_and_bottlenecks PASSED                     [  3%]
tests/api/analytics/test_analytics_api.py::test_asset_history_search_and_aggregates PASSED                                 [  4%]
tests/api/analytics/test_analytics_api.py::test_top_entities_and_email_masking PASSED                                      [  5%]
tests/api/analytics/test_analytics_api.py::test_cost_analytics_returns_expected_totals PASSED                              [  5%]
tests/api/analytics/test_analytics_api.py::test_trends_and_forecast_are_deterministic PASSED                               [  6%]
tests/api/analytics/test_analytics_api.py::test_alerts_endpoint_triggers_and_is_configurable PASSED                        [  7%]
tests/api/analytics/test_analytics_api.py::test_analytics_invalid_params_and_permissions PASSED                            [  8%]
tests/api/test_audit_stream.py::test_match_filters_happy_path <- D:\IIB ATV\tests\api\test_audit_stream.py PASSED          [  9%]
tests/api/test_audit_stream.py::test_match_filters_rejects_mismatches[kwargs0-event0] <- D:\IIB ATV\tests\api\test_audit_stream.py PASSED [ 10%]
tests/api/test_audit_stream.py::test_match_filters_rejects_mismatches[kwargs1-event1] <- D:\IIB ATV\tests\api\test_audit_stream.py PASSED [ 10%]
tests/api/test_audit_stream.py::test_match_filters_rejects_mismatches[kwargs2-event2] <- D:\IIB ATV\tests\api\test_audit_stream.py PASSED [ 11%]
tests/api/test_audit_stream.py::test_match_filters_rejects_mismatches[kwargs3-event3] <- D:\IIB ATV\tests\api\test_audit_stream.py PASSED [ 12%]
tests/api/test_audit_stream.py::test_match_filters_rejects_mismatches[kwargs4-event4] <- D:\IIB ATV\tests\api\test_audit_stream.py PASSED [ 13%]
tests/api/test_audit_stream.py::test_stream_audit_emits_retry_and_event <- D:\IIB ATV\tests\api\test_audit_stream.py PASSED [ 14%]
tests/core/test_email.py::test_send_email_rejects_empty_recipient <- D:\IIB ATV\tests\core\test_email.py PASSED            [ 15%]
tests/core/test_email.py::test_send_email_rejects_invalid_recipient <- D:\IIB ATV\tests\core\test_email.py PASSED          [ 15%]
tests/core/test_email.py::test_send_email_success <- D:\IIB ATV\tests\core\test_email.py PASSED                            [ 16%]
tests/core/test_email.py::test_send_email_maps_recipients_refused <- D:\IIB ATV\tests\core\test_email.py PASSED            [ 17%]
tests/core/test_email.py::test_send_email_maps_authentication_error <- D:\IIB ATV\tests\core\test_email.py PASSED          [ 18%]
tests/core/test_email.py::test_send_email_maps_smtp_exception <- D:\IIB ATV\tests\core\test_email.py PASSED                [ 19%]
tests/core/test_email.py::test_send_email_raises_for_rejected_result <- D:\IIB ATV\tests\core\test_email.py PASSED         [ 20%]
tests/middlewares/test_audit_middleware.py::test_get_level_boundaries <- D:\IIB ATV\tests\middlewares\test_audit_middleware.py PASSED [ 21%]
tests/middlewares/test_audit_middleware.py::test_audit_middleware_passes_through_non_http_scope <- D:\IIB ATV\tests\middlewares\test_audit_middleware.py PASSED [ 21%]
tests/middlewares/test_audit_middleware.py::test_audit_middleware_prod_enqueues_task <- D:\IIB ATV\tests\middlewares\test_audit_middleware.py PASSED [ 22%]
tests/repositories/test_analytics_repositories.py::test_region_repository_returns_correct_overview <- D:\IIB ATV\tests\repositories\test_analytics_repositories.py PASSED [ 23%]
tests/repositories/test_analytics_repositories.py::test_assignment_repository_aggregates_and_filters <- D:\IIB ATV\tests\repositories\test_analytics_repositories.py PASSED [ 24%]
tests/repositories/test_analytics_repositories.py::test_transfer_repository_metrics_and_bottlenecks <- D:\IIB ATV\tests\repositories\test_analytics_repositories.py PASSED [ 25%]
tests/repositories/test_asset_assignment_repo_unit.py::test_get_asset_returns_scalar_one_or_none PASSED                    [ 26%]
tests/repositories/test_asset_assignment_repo_unit.py::test_create_assignment_adds_and_flushes PASSED                      [ 26%]
tests/repositories/test_asset_assignment_repo_unit.py::test_close_assignment_sets_unassigned_at PASSED                     [ 27%]
tests/services/test_alert_analytics_service.py::test_alert_service_uses_configurable_thresholds <- D:\IIB ATV\tests\services\test_alert_analytics_service.py PASSED [ 28%]
tests/services/test_asset_assignment_service_unit.py::test_assign_asset_success PASSED                                     [ 29%]
tests/services/test_asset_assignment_service_unit.py::test_assign_asset_maps_lock_error PASSED                             [ 30%]
tests/services/test_asset_assignment_service_unit.py::test_assign_asset_raises_for_missing_asset PASSED                    [ 31%]
tests/services/test_asset_assignment_service_unit.py::test_unassign_asset_rejects_when_not_assigned PASSED                 [ 31%]
tests/services/test_asset_assignment_service_unit.py::test_reassign_asset_closes_active_and_delegates PASSED               [ 32%]
tests/services/test_top_analytics_service.py::test_top_users_masks_email_for_non_admin <- D:\IIB ATV\tests\services\test_top_analytics_service.py PASSED [ 33%]
tests/services/test_top_analytics_service.py::test_top_users_keeps_email_for_admin <- D:\IIB ATV\tests\services\test_top_analytics_service.py PASSED [ 34%]
tests/test_approval_hardening.py::test_double_approve_fails PASSED                                                         [ 35%]
tests/test_approval_hardening.py::test_replay_after_approve_fails PASSED                                                   [ 36%]
tests/test_approval_hardening.py::test_invalid_approval_payload_fails PASSED                                               [ 36%]
tests/test_approvals_bulk_export.py::test_create_and_approve_archive_request PASSED                                        [ 37%]
tests/test_approvals_bulk_export.py::test_reject_transfer_approval_request PASSED                                          [ 38%]
tests/test_approvals_bulk_export.py::test_bulk_assign_partial_success PASSED                                               [ 39%]
tests/test_approvals_bulk_export.py::test_export_assets_csv_with_filter PASSED                                             [ 40%]
tests/test_approvals_bulk_export.py::test_export_assets_json_returns_filtered_payload PASSED                               [ 41%]
tests/test_assets_domain.py::test_asset_assignment_flow PASSED                                                             [ 42%]
tests/test_assets_domain.py::test_asset_transfer_flow PASSED                                                               [ 42%]
tests/test_assets_domain.py::test_repair_lifecycle_flow PASSED                                                             [ 43%]
tests/test_assets_domain.py::test_document_attach_and_delete_flow PASSED                                                   [ 44%]
tests/test_assets_domain.py::test_warehouse_move_rejects_incompatible_location PASSED                                      [ 45%]
tests/test_assets_domain.py::test_locked_asset_transfer_is_rejected PASSED                                                 [ 46%]
tests/test_audit_service.py::test_list_audit_logs_requires_authentication <- D:\IIB ATV\tests\test_audit_service.py PASSED [ 47%]
tests/test_audit_service.py::test_list_audit_logs_success_as_admin <- D:\IIB ATV\tests\test_audit_service.py PASSED        [ 47%]
tests/test_audit_service.py::test_audit_stats_returns_expected_counters <- D:\IIB ATV\tests\test_audit_service.py PASSED   [ 48%]
tests/test_audit_service_unit.py::test_create_audit_log <- D:\IIB ATV\tests\test_audit_service_unit.py PASSED              [ 49%]
tests/test_audit_service_unit.py::test_list_audit_logs_empty <- D:\IIB ATV\tests\test_audit_service_unit.py PASSED         [ 50%]
tests/test_audit_service_unit.py::test_list_audit_logs_with_data <- D:\IIB ATV\tests\test_audit_service_unit.py PASSED     [ 51%]
tests/test_audit_service_unit.py::test_filter_by_user_id <- D:\IIB ATV\tests\test_audit_service_unit.py PASSED             [ 52%]
tests/test_audit_service_unit.py::test_filter_by_status_code <- D:\IIB ATV\tests\test_audit_service_unit.py PASSED         [ 52%]
tests/test_audit_service_unit.py::test_filter_by_search <- D:\IIB ATV\tests\test_audit_service_unit.py PASSED              [ 53%]
tests/test_audit_service_unit.py::test_get_by_request_id <- D:\IIB ATV\tests\test_audit_service_unit.py PASSED             [ 54%]
tests/test_audit_service_unit.py::test_get_errors <- D:\IIB ATV\tests\test_audit_service_unit.py PASSED                    [ 55%]
tests/test_audit_service_unit.py::test_get_stats <- D:\IIB ATV\tests\test_audit_service_unit.py PASSED                     [ 56%]
tests/test_audit_service_unit.py::test_pagination <- D:\IIB ATV\tests\test_audit_service_unit.py PASSED                    [ 57%]
tests/test_auth.py::test_login_success <- D:\IIB ATV\tests\test_auth.py PASSED                                             [ 57%]
tests/test_auth.py::test_login_invalid_password <- D:\IIB ATV\tests\test_auth.py PASSED                                    [ 58%]
tests/test_auth_security.py::test_refresh_token_reuse_attack PASSED                                                        [ 59%]
tests/test_auth_security.py::test_logout_blacklists_access_token PASSED                                                    [ 60%]
tests/test_auth_security.py::test_logout_all_revokes_all_sessions PASSED                                                   [ 61%]
tests/test_auth_security.py::test_access_token_cannot_be_used_as_refresh PASSED                                            [ 62%]
tests/test_auth_security.py::test_expired_refresh_token PASSED                                                             [ 63%]
tests/test_auth_security.py::test_revoke_single_session PASSED                                                             [ 63%]
tests/test_auth_security.py::test_refresh_same_device_ok PASSED                                                            [ 64%]
tests/test_auth_security.py::test_refresh_different_device_invalid PASSED                                                  [ 65%]
tests/test_bulk_operations.py::test_bulk_partial_success <- D:\IIB ATV\tests\test_bulk_operations.py PASSED                [ 66%]
tests/test_bulk_operations.py::test_bulk_limit_exceeded <- D:\IIB ATV\tests\test_bulk_operations.py PASSED                 [ 67%]
tests/test_bulk_operations.py::test_bulk_invalid_items_return_failed_entries <- D:\IIB ATV\tests\test_bulk_operations.py PASSED [ 68%]
tests/test_concurrency.py::test_assign_race_keeps_single_active_assignment PASSED                                          [ 68%]
tests/test_concurrency.py::test_row_lock_is_applied_for_assignment_repo PASSED                                             [ 69%]
tests/test_export.py::test_csv_export <- D:\IIB ATV\tests\test_export.py PASSED                                            [ 70%]
tests/test_export.py::test_export_row_limit <- D:\IIB ATV\tests\test_export.py PASSED                                      [ 71%]
tests/test_export.py::test_export_permissions <- D:\IIB ATV\tests\test_export.py PASSED                                    [ 72%]
tests/test_rbac.py::test_create_role <- D:\IIB ATV\tests\test_rbac.py PASSED                                               [ 73%]
tests/test_rbac.py::test_duplicate_role_code <- D:\IIB ATV\tests\test_rbac.py PASSED                                       [ 73%]
tests/test_rbac.py::test_set_permissions <- D:\IIB ATV\tests\test_rbac.py PASSED                                           [ 74%]
tests/test_rbac.py::test_delete_role_with_users_forbidden <- D:\IIB ATV\tests\test_rbac.py PASSED                          [ 75%]
tests/test_security.py::test_forgot_password_existing_user <- D:\IIB ATV\tests\test_security.py PASSED                     [ 76%]
tests/test_security.py::test_forgot_password_non_existing_user <- D:\IIB ATV\tests\test_security.py PASSED                 [ 77%]
tests/test_security.py::test_reset_password_success <- D:\IIB ATV\tests\test_security.py PASSED                            [ 78%]
tests/test_security.py::test_reset_password_invalid_token <- D:\IIB ATV\tests\test_security.py PASSED                      [ 78%]
tests/test_security.py::test_reset_token_reuse <- D:\IIB ATV\tests\test_security.py PASSED                                 [ 79%]
tests/test_security.py::test_password_changed_after_reset <- D:\IIB ATV\tests\test_security.py PASSED                      [ 80%]
tests/test_security.py::test_sessions_revoked_after_password_reset <- D:\IIB ATV\tests\test_security.py PASSED             [ 81%]
tests/test_security.py::test_forgot_password_rate_limit <- D:\IIB ATV\tests\test_security.py PASSED                        [ 82%]
tests/test_sessions.py::test_list_sessions <- D:\IIB ATV\tests\test_sessions.py PASSED                                     [ 83%]
tests/test_sessions.py::test_revoke_session <- D:\IIB ATV\tests\test_sessions.py PASSED                                    [ 84%]
tests/test_sessions.py::test_revoke_session_not_owned <- D:\IIB ATV\tests\test_sessions.py PASSED                          [ 84%]
tests/test_sessions.py::test_revoke_current_session_forbidden <- D:\IIB ATV\tests\test_sessions.py PASSED                  [ 85%]
tests/test_sessions.py::test_logout_all_sessions <- D:\IIB ATV\tests\test_sessions.py PASSED                               [ 86%]
tests/test_sessions.py::test_cleanup_sessions <- D:\IIB ATV\tests\test_sessions.py PASSED                                  [ 87%]
tests/test_sessions.py::test_session_is_active_flag <- D:\IIB ATV\tests\test_sessions.py PASSED                            [ 88%]
tests/utils/test_validators.py::test_validate_name_strips_and_returns_value <- D:\IIB ATV\tests\utils\test_validators.py PASSED [ 89%]
tests/utils/test_validators.py::test_validate_name_rejects_invalid_values[-Name cannot be empty] <- D:\IIB ATV\tests\utils\test_validators.py PASSED [ 89%]
tests/utils/test_validators.py::test_validate_name_rejects_invalid_values[ -Name cannot be empty] <- D:\IIB ATV\tests\utils\test_validators.py PASSED [ 90%]
tests/utils/test_validators.py::test_validate_name_rejects_invalid_values[a-Name too short] <- D:\IIB ATV\tests\utils\test_validators.py PASSED [ 91%]
tests/utils/test_validators.py::test_validate_name_rejects_invalid_values[!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!-Name is too long] <- D:\IIB ATV\tests\utils\test_validators.py PASSED [ 92%]
tests/utils/test_validators.py::test_validate_name_rejects_invalid_values[!!!-Invalid name] <- D:\IIB ATV\tests\utils\test_validators.py PASSED [ 93%]
tests/utils/test_validators.py::test_normalize_name <- D:\IIB ATV\tests\utils\test_validators.py PASSED                    [ 94%]
tests/utils/test_validators.py::test_ensure_unique_name_raises_when_found <- D:\IIB ATV\tests\utils\test_validators.py PASSED [ 94%]
tests/utils/test_validators.py::test_ensure_unique_code_raises_when_found <- D:\IIB ATV\tests\utils\test_validators.py PASSED [ 95%]
tests/utils/test_validators.py::test_safe_create_returns_repo_result <- D:\IIB ATV\tests\utils\test_validators.py PASSED   [ 96%]
tests/utils/test_validators.py::test_safe_create_maps_integrity_error <- D:\IIB ATV\tests\utils\test_validators.py PASSED  [ 97%]
tests/utils/test_validators.py::test_safe_create_maps_unknown_error <- D:\IIB ATV\tests\utils\test_validators.py PASSED    [ 98%]
tests/utils/test_validators.py::test_validate_and_prepare_success <- D:\IIB ATV\tests\utils\test_validators.py PASSED      [ 99%]
tests/utils/test_validators.py::test_validate_and_prepare_rejects_empty_slug <- D:\IIB ATV\tests\utils\test_validators.py PASSED [100%]

================================================ 119 passed in 145.02s (0:02:25) ================================================
task: [test-cov] uv run --no-sync coverage report -m --fail-under=80
Name                                                            Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------------------------
src\__init__.py                                                     0      0   100%
src\api\__init__.py                                                 0      0   100%
src\api\dependencies\__init__.py                                    0      0   100%
src\api\dependencies\analytics.py                                 131     23    82%   76, 80, 86, 92, 98, 104, 110, 116, 249, 255, 261, 267, 273, 279, 285, 291, 297, 303, 309, 315, 326, 342, 350
src\api\dependencies\assets\__init__.py                             0      0   100%
src\api\dependencies\assets\asset_approval.py                      20      0   100%
src\api\dependencies\assets\asset_assignment.py                    11      0   100%
src\api\dependencies\assets\asset_category.py                       9      2    78%   12, 18
src\api\dependencies\assets\asset_class.py                          9      2    78%   14, 20
src\api\dependencies\assets\asset_export.py                         6      0   100%
src\api\dependencies\assets\asset_history.py                        9      0   100%
src\api\dependencies\assets\asset_model.py                         13      2    85%   17, 25
src\api\dependencies\assets\asset_repair.py                        10      0   100%
src\api\dependencies\assets\asset_transfer.py                      11      0   100%
src\api\dependencies\assets\asset_warehouse.py                     11      0   100%
src\api\dependencies\assets\assets.py                              18      0   100%
src\api\dependencies\assets\manufacturer.py                         9      2    78%   12, 18
src\api\dependencies\audit.py                                       9      0   100%
src\api\dependencies\auth\__init__.py                               0      0   100%
src\api\dependencies\auth\auth.py                                  11      0   100%
src\api\dependencies\auth\security.py                              13      0   100%
src\api\dependencies\documents\__init__.py                          0      0   100%
src\api\dependencies\documents\document.py                         14      0   100%
src\api\dependencies\events\__init__.py                             0      0   100%
src\api\dependencies\events\asset.py                               11      0   100%
src\api\dependencies\events\asset_repair.py                        10      0   100%
src\api\dependencies\events\asset_transfer.py                      10      0   100%
src\api\dependencies\events\base.py                                 6      0   100%
src\api\dependencies\events\warehouse.py                           10      0   100%
src\api\dependencies\notifications\__init__.py                      0      0   100%
src\api\dependencies\notifications\notification.py                 41      6    85%   33, 47-49, 74, 81-83
src\api\dependencies\organizations\__init__.py                      0      0   100%
src\api\dependencies\organizations\regions.py                       9      2    78%   10, 16
src\api\dependencies\organizations\services.py                      9      2    78%   10, 16
src\api\dependencies\paginations.py                                 4      1    75%   9
src\api\dependencies\rbac.py                                        9      0   100%
src\api\dependencies\sessions.py                                    9      0   100%
src\api\dependencies\users.py                                      10      1    90%   19
src\api\routers\v1.py                                              78      0   100%
src\api\v1\__init__.py                                              0      0   100%
src\api\v1\analytics\__init__.py                                    0      0   100%
src\api\v1\analytics\_utils.py                                     60     15    75%   26-29, 40, 66-67, 71, 73, 89-108
src\api\v1\analytics\alerts.py                                     21      2    90%   71-74
src\api\v1\analytics\analytics_endpoints.py                        57     20    65%   37, 43, 61-62, 78-79, 95-96, 112-113, 128-129, 144-145, 161-162, 178-179, 195-196
src\api\v1\analytics\approvals.py                                  15      2    87%   30-33
src\api\v1\analytics\asset_history.py                              34      2    94%   165-168
src\api\v1\analytics\assets.py                                     28      8    71%   27, 33, 45-46, 58-59, 71-72
src\api\v1\analytics\assignment_analytics.py                       47      4    91%   116-119, 149-152
src\api\v1\analytics\costs.py                                      27      0   100%
src\api\v1\analytics\dashboard.py                                  15     15     0%   1-29
src\api\v1\analytics\dashboard\__init__.py                          0      0   100%
src\api\v1\analytics\dashboard\overview.py                         18      0   100%
src\api\v1\analytics\dashboard\regions.py                          16      2    88%   32-35
src\api\v1\analytics\dashboard\repairs.py                          21      4    81%   32-35, 54-60
src\api\v1\analytics\dashboard\router.py                           12      0   100%
src\api\v1\analytics\dashboard\services.py                         16      2    88%   32-35
src\api\v1\analytics\dashboard\top_assets.py                       16      2    88%   32-35
src\api\v1\analytics\documents.py                                  15      2    87%   26-29
src\api\v1\analytics\forecast.py                                   22      2    91%   61-64
src\api\v1\analytics\regions.py                                    27      0   100%
src\api\v1\analytics\repairs.py                                    15      2    87%   26-29
src\api\v1\analytics\reports.py                                    15      2    87%   26-29
src\api\v1\analytics\top.py                                        28      0   100%
src\api\v1\analytics\transfer_analytics.py                         51      6    88%   116-119, 148-151, 265-268
src\api\v1\analytics\transfers.py                                  15     15     0%   1-29
src\api\v1\analytics\trends.py                                     26      4    85%   30-33, 52-55
src\api\v1\analytics\utilization.py                                15      2    87%   26-29
src\api\v1\approvals\__init__.py                                    1      0   100%
src\api\v1\approvals\approvals.py                                  25      1    96%   34
src\api\v1\approvals\requests.py                                   27      1    96%   106
src\api\v1\assets\__init__.py                                       0      0   100%
src\api\v1\assets\asset.py                                         65      9    86%   71, 108, 132-134, 166, 176-177, 192
src\api\v1\assets\asset_categories.py                              18      4    78%   21, 29, 37-38
src\api\v1\assets\asset_classes.py                                 18      4    78%   18, 26, 34-35
src\api\v1\assets\asset_documents.py                               23      2    91%   29, 59
src\api\v1\assets\asset_model.py                                   18      4    78%   17, 25, 33-34
src\api\v1\assets\asset_repairs.py                                 22      1    95%   71
src\api\v1\assets\asset_warehouse.py                               18      1    94%   39
src\api\v1\assets\manufacturer.py                                  17      4    76%   17, 25, 33-34
src\api\v1\audit\__init__.py                                        0      0   100%
src\api\v1\audit\audit.py                                          41      5    88%   62, 72, 82, 92, 101
src\api\v1\audit\audit_stream.py                                   54     12    78%   67, 71-77, 82, 91, 93, 96, 101-102
src\api\v1\auth\auth.py                                            33      8    76%   31-41, 53-63, 76-78, 89-90
src\api\v1\auth\sessions.py                                        29      4    86%   34, 43, 52, 55
src\api\v1\expenses.py                                             49     19    61%   43-44, 68-69, 83-84, 99-100, 114-116, 130-131, 145-146, 160-161, 174-175
src\api\v1\notifications.py                                        51     26    49%   34-60, 70, 83-87, 95-96, 104-105
src\api\v1\organization\__init__.py                                 0      0   100%
src\api\v1\organization\regions.py                                 22      7    68%   28, 43, 57-62
src\api\v1\organization\services.py                                22      7    68%   27, 41-46, 60
src\api\v1\rbac\__init__.py                                         0      0   100%
src\api\v1\rbac\rbac.py                                            28      4    86%   31, 40, 60, 70
src\api\v1\users\__init__.py                                        0      0   100%
src\api\v1\users\security.py                                       17      2    88%   29, 47
src\api\v1\users\user.py                                           82     34    59%   27-33, 54-55, 65-66, 76-81, 92-93, 102-104, 116-117, 128-129, 140-144, 154-158, 168-172, 182-186
src\app.py                                                         56      3    95%   65, 75, 79
src\core\__init__.py                                                0      0   100%
src\core\admin\__init__.py                                          0      0   100%
src\core\admin\auth.py                                             28     17    39%   12-28, 31-33, 36
src\core\admin\base.py                                              9      0   100%
src\core\admin\registry.py                                         42      0   100%
src\core\admin\views\__init__.py                                    0      0   100%
src\core\admin\views\assets\__init__.py                             1      0   100%
src\core\admin\views\assets\approvals.py                            8      0   100%
src\core\admin\views\assets\assets.py                              78      0   100%
src\core\admin\views\assets\dashboard.py                           11      2    82%   14-53
src\core\admin\views\assets\documents.py                           17      0   100%
src\core\admin\views\assets\misc.py                                30      0   100%
src\core\admin\views\assets\org.py                                 19      0   100%
src\core\admin\views\assets\repairs.py                             15      0   100%
src\core\admin\views\users\__init__.py                              3      0   100%
src\core\admin\views\users\permission.py                           10      0   100%
src\core\admin\views\users\role.py                                 10      0   100%
src\core\admin\views\users\user.py                                 34     12    65%   18-44, 69-77
src\core\audit\__init__.py                                          0      0   100%
src\core\audit\stream.py                                           50     32    36%   20-24, 27-34, 39, 42-68
src\core\cache\__init__.py                                          0      0   100%
src\core\cache\backends.py                                         94     45    52%   28-29, 39, 45-46, 56-64, 71-73, 84, 87-92, 95-99, 102, 105, 108-116, 119-124, 127
src\core\cache\decorators.py                                       50     14    72%   10, 12, 48-56, 61, 64-65, 81-84
src\core\cache\manager.py                                          93     10    89%   41, 51, 56-57, 68-71, 141, 145, 148
src\core\celery.py                                                 12      0   100%
src\core\config.py                                                 92      4    96%   126, 131-141
src\core\database\__init__.py                                       0      0   100%
src\core\database\db_async.py                                      10      3    70%   15-17, 29
src\core\database\db_sync.py                                       11      1    91%   27
src\core\email.py                                                  30      0   100%
src\core\events\asset_events.py                                    22      2    91%   139, 201
src\core\events\base.py                                            21      6    71%   24-29, 40-41
src\core\events\document_events.py                                 14      0   100%
src\core\events\repair_events.py                                   21      4    81%   124-128
src\core\events\transfer_events.py                                 16      1    94%   80
src\core\events\warehouse_events.py                                13      0   100%
src\core\exceptions\__init__.py                                     0      0   100%
src\core\exceptions\base.py                                        13      0   100%
src\core\exceptions\errors.py                                      41      0   100%
src\core\exceptions\handlers.py                                    48     13    73%   104-126, 134-146
src\core\lifespan.py                                               18      9    50%   12-15, 20-24
src\core\logger.py                                                 19      3    84%   14, 24, 52
src\core\notifications\__init__.py                                  0      0   100%
src\core\notifications\builder.py                                  73     17    77%   28, 48, 60, 107, 117, 153, 192-196, 227, 242, 258, 274, 290, 306, 334
src\core\notifications\channels\db_channel.py                       6      0   100%
src\core\notifications\channels\websocket.py                       19     10    47%   12, 15-16, 19-22, 25-26, 30
src\core\notifications\channels\ws_channel.py                       7      0   100%
src\core\notifications\dispatcher.py                               12      3    75%   10, 15-16
src\core\notifications\router.py                                    9      6    33%   3, 6-10
src\core\notifications\types.py                                    24      0   100%
src\core\notifications\ws\backends\base.py                          3      0   100%
src\core\notifications\ws\backends\memory.py                       23     12    48%   13-14, 17-22, 26-30
src\core\notifications\ws\redis_listener.py                        16     10    38%   8-9, 12-22
src\core\observability\__init__.py                                  3      0   100%
src\core\observability\monitoring.py                               35     11    69%   31, 36, 41-42, 51-57, 62-63
src\core\observability\prometheus.py                               25      5    80%   27-29, 97-98
src\core\observability\sentry.py                                    7      4    43%   7-12
src\core\redis.py                                                   4      0   100%
src\core\requests.py                                                5      1    80%   8
src\core\security\__init__.py                                       0      0   100%
src\core\security\access_control.py                                61     33    46%   35-42, 50-57, 62-66, 76-77, 89-101, 106-110, 114-118
src\core\security\auth\__init__.py                                  0      0   100%
src\core\security\auth\dependencies.py                             34     11    68%   29, 44-64
src\core\security\auth\extractor.py                                11      0   100%
src\core\security\auth\ws_dependencies.py                          20     12    40%   16-33
src\core\security\blacklist.py                                     37      9    76%   25-26, 33, 36-40, 43, 56
src\core\security\jwt.py                                           35      3    91%   67, 84, 87
src\core\security\passwords.py                                     19      3    84%   57-59
src\core\security\rbac\__init__.py                                  0      0   100%
src\core\security\rbac\guards.py                                   20      4    80%   9-10, 20-21
src\core\security\rbac\permissions.py                             101     16    84%   124-125, 129-142, 347, 351, 355, 359
src\core\security\rbac\presets.py                                  53      0   100%
src\core\slowapi.py                                                28     15    46%   14-27, 32, 48-57
src\db\base.py                                                     30      6    80%   58-63
src\db\dependencies.py                                              8      4    50%   9-13
src\db\meta.py                                                      2      0   100%
src\db\models\__init__.py                                          11      1    91%   18
src\db\models\approvals\__init__.py                                 1      0   100%
src\db\models\approvals\approval_request.py                        23      0   100%
src\db\models\assets\__init__.py                                    8      0   100%
src\db\models\assets\asset.py                                      62      4    94%   173, 179, 181, 185
src\db\models\assets\asset_assignment.py                           18      1    94%   49
src\db\models\assets\asset_category.py                             16      1    94%   45
src\db\models\assets\asset_class.py                                14      1    93%   25
src\db\models\assets\asset_history.py                              16      1    94%   32
src\db\models\assets\asset_model.py                                30      3    90%   48, 54, 65
src\db\models\assets\asset_transfer.py                             29      1    97%   76
src\db\models\assets\manufacturer.py                               15      1    93%   27
src\db\models\audit\__init__.py                                     1      0   100%
src\db\models\audit\audit_log.py                                   19      0   100%
src\db\models\auth\__init__.py                                      1      0   100%
src\db\models\auth\password_reset.py                               11      0   100%
src\db\models\documents\__init__.py                                 2      0   100%
src\db\models\documents\document.py                                21      1    95%   59
src\db\models\documents\document_file.py                           15      1    93%   32
src\db\models\enums.py                                             57      0   100%
src\db\models\expenses.py                                          22      0   100%
src\db\models\mixins\__init__.py                                    0      0   100%
src\db\models\mixins\slug_mixin.py                                 12      1    92%   12
src\db\models\notifications\__init__.py                             0      0   100%
src\db\models\notifications\notification.py                        18      0   100%
src\db\models\org\__init__.py                                       2      0   100%
src\db\models\org\region.py                                        16      0   100%
src\db\models\org\service.py                                       12      0   100%
src\db\models\refresh_token.py                                     18      0   100%
src\db\models\repairs\__init__.py                                   2      0   100%
src\db\models\repairs\repair.py                                    27      1    96%   58
src\db\models\repairs\repair_part.py                               18      1    94%   32
src\db\models\system\__init__.py                                    1      0   100%
src\db\models\system\system_config.py                               8      0   100%
src\db\models\users\__init__.py                                     2      0   100%
src\db\models\users\permission.py                                  26      2    92%   71, 99
src\db\models\users\user.py                                        61      3    95%   70, 123, 128
src\db\models\warehouse\__init__.py                                 1      0   100%
src\db\models\warehouse\warehouse.py                               19      1    95%   46
src\dev.py                                                          2      2     0%   1-3
src\main.py                                                         7      7     0%   6-24
src\middlewares\__init__.py                                         0      0   100%
src\middlewares\audit.py                                           69     15    78%   52-56, 59-67, 110
src\middlewares\logging.py                                         29      7    76%   12-13, 23, 39-42
src\middlewares\metrics.py                                         33      4    88%   24-25, 72, 74
src\middlewares\request_id.py                                      25      3    88%   17-18, 27
src\repositories\__init__.py                                        0      0   100%
src\repositories\analytics\__init__.py                              0      0   100%
src\repositories\analytics\alert_analytics_repo.py                 26      4    85%   26, 41, 73, 88
src\repositories\analytics\approval_analytics_repo.py              18      8    56%   15-20, 23-24
src\repositories\analytics\asset_analytics_repo.py                 36     22    39%   23-28, 37-98, 114-138
src\repositories\analytics\asset_assignment_analytics_repo.py      71     23    68%   34, 39, 42, 45, 48-49, 104-124, 129-167, 186-191, 201, 259-260, 271-272
src\repositories\analytics\asset_history_analytics_repo.py         54     16    70%   27, 30, 33, 36, 39, 85-89, 113-141, 167-168, 181-182
src\repositories\analytics\asset_transfer_analytics_repo.py        88     28    68%   31, 34, 37, 40, 45, 50, 55, 58, 61, 64, 67-68, 111-115, 121-145, 151-164, 336-392
src\repositories\analytics\cost_analytics_repo.py                  31      6    81%   52-55, 90-93, 137-140
src\repositories\analytics\dashboard\region_repo.py                10      3    70%   10, 13-42
src\repositories\analytics\dashboard\repair_repo.py                13      5    62%   10, 13-20, 23-38
src\repositories\analytics\dashboard\service_repo.py               11      3    73%   11, 14-27
src\repositories\analytics\dashboard\top_assets_repo.py            10      3    70%   10, 13-24
src\repositories\analytics\document_analytics_repo.py              21     11    48%   20-25, 35-69
src\repositories\analytics\forecast_analytics_repo.py               3      0   100%
src\repositories\analytics\region_analytics_repo.py                42      7    83%   139-217
src\repositories\analytics\repair_analytics_repo.py                30     17    43%   21-26, 30-35, 46-73
src\repositories\analytics\top_analytics_repo.py                   30      3    90%   63, 113, 175
src\repositories\analytics\transfer_analytics_repo.py              30     17    43%   21-26, 30-35, 46-75
src\repositories\analytics\trend_analytics_repo.py                 30      8    73%   21, 25-37, 40-50, 81
src\repositories\analytics\utilization_analytics_repo.py           24     11    54%   23-28, 37-79
src\repositories\assets\__init__.py                                 0      0   100%
src\repositories\assets\approval_repo.py                           30     10    67%   23-24, 27, 53-74
src\repositories\assets\asset_assignment_repo.py                   35      1    97%   31
src\repositories\assets\asset_category_repo.py                     27     11    59%   13, 16, 21, 26, 31, 36, 41-44, 48
src\repositories\assets\asset_class_repo.py                        23     10    57%   12, 15, 20, 25, 30, 35-38, 41
src\repositories\assets\asset_history_repo.py                      15      2    87%   30-31
src\repositories\assets\asset_model_repo.py                        24     10    58%   14, 17, 22, 27, 32, 40-43, 47
src\repositories\assets\asset_repo.py                             114     30    74%   43, 46-60, 89, 93, 96, 99, 102, 105, 108, 111, 114, 155, 167, 179, 189, 196-197, 201-202, 205, 217-218, 221-224
src\repositories\assets\asset_transfer_repo.py                     36      5    86%   22, 53, 68, 73-74
src\repositories\assets\manufacturer_repo.py                       22     10    55%   10, 13, 18, 23, 28, 33-36, 39
src\repositories\assets\repair_repo.py                             47     14    70%   22, 47, 54, 83-84, 89-92, 97-106
src\repositories\audit\__init__.py                                  0      0   100%
src\repositories\audit\audit_repo.py                               94     22    77%   23-25, 38, 46, 55, 58, 61, 64, 67, 105-110, 129-142, 145-158
src\repositories\auth\__init__.py                                   0      0   100%
src\repositories\auth\auth_repo.py                                 25      5    80%   21, 31, 39, 66-69
src\repositories\auth\session_repo.py                              36     12    67%   23-25, 31, 42, 53, 56-65, 71, 74-79
src\repositories\base.py                                           42     12    71%   16, 22-23, 36-37, 44-45, 52-56
src\repositories\documents\__init__.py                              0      0   100%
src\repositories\documents\document_repo.py                        31      9    71%   18, 41-42, 46, 51-60
src\repositories\expenses.py                                      107     85    21%   23, 29-44, 58-97, 101-103, 107-110, 114-120, 124-130, 134-140, 144-148, 152-158, 162-168, 172-174, 178-185, 191-208
src\repositories\notifications\__init__.py                          0      0   100%
src\repositories\notifications\notification_repo.py                28     12    57%   17-18, 27-34, 39, 45, 52, 59-65
src\repositories\organization\__init__.py                           0      0   100%
src\repositories\organization\region_repo.py                       53     37    30%   16, 19-22, 25, 28-39, 42-51, 54, 64-81
src\repositories\organization\service_repo.py                      25     11    56%   16, 19-20, 23-26, 29-36, 49
src\repositories\rbac\__init__.py                                   0      0   100%
src\repositories\rbac\rbac_repo.py                                 48     16    67%   17, 31, 38, 45-46, 49-58, 61, 65, 69
src\repositories\users\__init__.py                                  0      0   100%
src\repositories\users\password_reset_repo.py                      22      3    86%   19-20, 41
src\repositories\users\user_repo.py                                52     20    62%   34, 46, 54-55, 68, 71, 74-77, 80-83, 86-89, 92, 97, 102, 107-109
src\repositories\warehouse\warehouse_repo.py                       15      0   100%
src\schemas\__init__.py                                             0      0   100%
src\schemas\analytics\__init__.py                                   0      0   100%
src\schemas\analytics\alerts.py                                    21      0   100%
src\schemas\analytics\approval.py                                   5      5     0%   1-7
src\schemas\analytics\asset.py                                     17     17     0%   1-25
src\schemas\analytics\asset_assignment_analytics.py                95      0   100%
src\schemas\analytics\asset_history.py                             49      0   100%
src\schemas\analytics\asset_transfer_analytics.py                 121      0   100%
src\schemas\analytics\common.py                                    37      0   100%
src\schemas\analytics\costs.py                                     24      0   100%
src\schemas\analytics\dashboard\overview.py                        27      0   100%
src\schemas\analytics\dashboard\region.py                          15      0   100%
src\schemas\analytics\dashboard\repairs.py                         15      0   100%
src\schemas\analytics\dashboard\services.py                         8      0   100%
src\schemas\analytics\dashboard\top_assets.py                       4      0   100%
src\schemas\analytics\document.py                                   6      6     0%   1-8
src\schemas\analytics\forecast.py                                  11      0   100%
src\schemas\analytics\regions.py                                   49      0   100%
src\schemas\analytics\repair.py                                    10     10     0%   1-14
src\schemas\analytics\report.py                                    10     10     0%   1-15
src\schemas\analytics\top.py                                       33      0   100%
src\schemas\analytics\transfer.py                                  10     10     0%   1-15
src\schemas\analytics\trends.py                                    19      0   100%
src\schemas\analytics\utilization.py                               20     20     0%   1-28
src\schemas\assets\approvals.py                                    38      0   100%
src\schemas\assets\asset_assignments.py                            13      0   100%
src\schemas\assets\asset_category.py                               12      0   100%
src\schemas\assets\asset_class.py                                  11      0   100%
src\schemas\assets\asset_model.py                                  17      0   100%
src\schemas\assets\asset_transfers.py                              30      1    97%   17
src\schemas\assets\assets.py                                      119      0   100%
src\schemas\assets\bulk.py                                         22      0   100%
src\schemas\assets\manufacturer.py                                 13      0   100%
src\schemas\assets\repairs.py                                      40      0   100%
src\schemas\assets\warehouses.py                                    4      0   100%
src\schemas\audit\__init__.py                                       1      0   100%
src\schemas\audit\audit.py                                         71      1    99%   81
src\schemas\auth\__init__.py                                        2      0   100%
src\schemas\auth\auth.py                                           51      4    92%   22, 32, 35, 44
src\schemas\auth\security.py                                       19      4    79%   14, 17, 20, 23
src\schemas\common.py                                               5      0   100%
src\schemas\documents\__init__.py                                   1      0   100%
src\schemas\documents\documents.py                                 36      0   100%
src\schemas\expenses.py                                            70      0   100%
src\schemas\notifications\__init__.py                               0      0   100%
src\schemas\notifications\notification.py                          24      0   100%
src\schemas\pagination.py                                          28      0   100%
src\schemas\rbac\__init__.py                                        0      0   100%
src\schemas\rbac\rbac.py                                           22      0   100%
src\schemas\users\__init__.py                                       2      0   100%
src\schemas\users\sessions.py                                      17      0   100%
src\schemas\users\users.py                                         36      0   100%
src\scripts\__init__.py                                             0      0   100%
src\scripts\bootstrap\__init__.py                                   0      0   100%
src\scripts\bootstrap\rbac.py                                      51     46    10%   25-121
src\scripts\cleanup\__init__.py                                     0      0   100%
src\scripts\cleanup\tokens.py                                      17     17     0%   1-34
src\scripts\cli.py                                                 23     23     0%   1-43
src\scripts\runner.py                                              11     11     0%   1-18
src\scripts\users\__init__.py                                       0      0   100%
src\scripts\users\create_superadmin.py                             45     45     0%   3-98
src\services\__init__.py                                            0      0   100%
src\services\analytics\__init__.py                                  0      0   100%
src\services\analytics\_scope.py                                   10      6    40%   7-20
src\services\analytics\alert_analytics_service.py                  28      0   100%
src\services\analytics\alert_service.py                            25     13    48%   20-22, 25, 28-64
src\services\analytics\approval_analytics_service.py               13      6    54%   9, 12-16
src\services\analytics\asset_analytics_service.py                  28     17    39%   15, 19-32, 37-45, 66-83
src\services\analytics\asset_assignment_analytics_service.py       66     29    56%   37, 48-76, 91-121, 135, 141-146, 155-195, 210-221
src\services\analytics\asset_history_analytics_service.py          13      4    69%   26-40, 55-65
src\services\analytics\asset_transfer_analytics_service.py         53     25    53%   41-43, 52, 59-63, 73-109, 126-160, 183-191, 201-203, 265-268
src\services\analytics\cost_analytics_service.py                   21      6    71%   20-32, 42-55, 65-77
src\services\analytics\dashboard\__init__.py                        0      0   100%
src\services\analytics\dashboard\overview_service.py               15      3    80%   32-35
src\services\analytics\dashboard\region_service.py                 12      8    33%   6, 9-34
src\services\analytics\dashboard\repair_service.py                 10      5    50%   6, 9-11, 25-27
src\services\analytics\dashboard\service_service.py                 8      3    62%   7, 10-12
src\services\analytics\dashboard\top_assets_service.py              8      3    62%   7, 10-12
src\services\analytics\document_analytics_service.py               11      3    73%   15, 18-19
src\services\analytics\forecast_analytics_service.py               24      8    67%   15, 23-25, 39-42
src\services\analytics\region_analytics_service.py                 33     17    48%   42, 46-72, 80-106
src\services\analytics\repair_analytics_service.py                 15      8    47%   9, 12-33
src\services\analytics\report_service.py                           24     10    58%   26-31, 34-39, 68-79
src\services\analytics\top_analytics_service.py                    31      4    87%   19, 21, 40, 84
src\services\analytics\transfer_analytics_service.py               13      6    54%   9, 12-34
src\services\analytics\trend_analytics_service.py                  57     12    79%   21, 30-32, 73, 84-86, 92-94, 102
src\services\analytics\utilization_analytics_service.py            20     13    35%   9, 12-36
src\services\approvals\__init__.py                                  0      0   100%
src\services\approvals\approval_service.py                        157     63    60%   61-63, 81-91, 115, 126-160, 171-194, 206-215, 233, 239, 255, 271, 280, 285, 288-300, 322, 325-326, 338-340, 359
src\services\assets\__init__.py                                     0      0   100%
src\services\assets\asset_assignment_service.py                    85     23    73%   33, 42, 45, 49-52, 55, 59, 62, 65, 68, 97, 106-121, 132-133, 136
src\services\assets\asset_category_service.py                      22     12    45%   10, 13, 16-23, 26-32
src\services\assets\asset_class_service.py                         23     12    48%   14, 17, 20-28, 31-39
src\services\assets\asset_history_service.py                       12      0   100%
src\services\assets\asset_model_service.py                         42     28    33%   27-29, 32, 36-73, 76-84
src\services\assets\asset_service.py                              156     98    37%   57-65, 76-79, 86-89, 101-106, 117-150, 155-203, 213-233, 236-254, 266-268, 280, 282, 284, 286-287, 289-293, 296-307, 318-322, 327, 332, 334, 338, 345
src\services\assets\asset_transfer_service.py                      92     74    20%   30-82, 92-137, 146-173
src\services\assets\bulk_asset_service.py                          64     16    75%   59-63, 99-100, 106, 108, 111, 119-125, 129, 132, 135
src\services\assets\export_service.py                              39      3    92%   18-19, 74
src\services\assets\manufacturer_service.py                        23     12    48%   12, 15, 18-27, 30-38
src\services\assets\repair_service.py                             122     90    26%   37-66, 76-125, 135-169, 178-213
src\services\assets\warehouse_service.py                           27     15    44%   23-54
src\services\audit\__init__.py                                      0      0   100%
src\services\audit\audit_service.py                                41      7    83%   53-54, 67-70, 75-78, 91
src\services\auth\__init__.py                                       0      0   100%
src\services\auth\auth_service.py                                  81     44    46%   31-58, 67-118, 127, 137-138, 150-153
src\services\auth\security_service.py                              51     26    49%   33-61, 67-82
src\services\dashboard\dashboard_service.py                        16      6    62%   19-22, 25-33
src\services\documents\__init__.py                                  0      0   100%
src\services\documents\document_service.py                         37     18    51%   28-60, 67-76, 86-92
src\services\expenses.py                                           47     29    38%   25, 31-33, 47-58, 70-73, 79-82, 86-88, 92-93, 100-101, 108-109, 116-122
src\services\notifications\__init__.py                              0      0   100%
src\services\notifications\notification_service.py                 33     15    55%   39, 48-50, 53-67, 70, 73
src\services\organization\__init__.py                               0      0   100%
src\services\organization\region_service.py                        21     12    43%   11, 14, 17-22, 25-28
src\services\organization\service_service.py                       13      4    69%   11, 14, 17, 20
src\services\rbac\__init__.py                                       0      0   100%
src\services\rbac\rbac_service.py                                  63     43    32%   17, 20-26, 33-46, 49-65, 69-76, 80, 85-98
src\services\repairs\__init__.py                                    0      0   100%
src\services\repairs\repair_service.py                             80     80     0%   3-298
src\services\users\__init__.py                                      0      0   100%
src\services\users\session_service.py                              22      8    64%   13, 17-26
src\services\users\user_service.py                                 60     38    37%   20-21, 24, 27, 30-33, 36-57, 60-69, 72-84, 92-98, 104, 107, 110
src\services\warehouse\__init__.py                                  0      0   100%
src\services\warehouse\warehouse_service.py                        73     73     0%   3-359
src\tasks\__init__.py                                               2      0   100%
src\tasks\audit_task.py                                            18     10    44%   12-22
src\tasks\email_task.py                                            11      7    36%   7-23
src\utils\__init__.py                                               0      0   100%
src\utils\helpers.py                                               10      0   100%
src\utils\reset_tokens.py                                           6      0   100%
src\utils\slug.py                                                   9      0   100%
src\utils\validators.py                                            41      0   100%
---------------------------------------------------------------------------------------------
TOTAL                                                            9554   2601    73%
Coverage failure: total of 73 is less than fail-under=80
task: Failed to run task "test-cov": exit status 2
(IIB ATV) PS E:\IIB ATV>
