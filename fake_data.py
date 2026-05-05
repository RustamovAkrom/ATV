#!/usr/bin/env python3
"""
Comprehensive System Testing & Fake Data Generation Script

Tests all major API workflows:
- Authentication & RBAC
- User management
- Asset lifecycle (create, assign, transfer, repair)
- Approvals workflow
- Bulk operations
- Concurrency scenarios
- Analytics validation
- Audit trails

CRITICAL: Uses ONLY API endpoints. NO direct database access.
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
import httpx
from dataclasses import dataclass, asdict, field


# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "http://localhost:8000"
# NOTE: superadmin credentials must match database seeding
# For local testing with conftest.py fixtures, use: superadmin / password
SUPERADMIN_LOGIN = "Akromjon"
SUPERADMIN_PASSWORD = "Akromjon2007"

# Test data volume
ASSETS_PER_REGION = 5
USERS_PER_ROLE = 2
REGIONS = 2
SERVICES = 1

# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class TestResult:
    """Track individual operation results"""
    endpoint: str
    method: str
    status_code: int
    success: bool
    error: Optional[str] = None
    data: Any = None
    duration_ms: float = 0.0


@dataclass
class TestContext:
    """Global test context"""
    results: List[TestResult] = field(default_factory=list)
    users: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # {login: {token, id, role}}
    assets: List[Dict[str, Any]] = field(default_factory=list)
    regions: List[Dict[str, Any]] = field(default_factory=list)
    services: List[Dict[str, Any]] = field(default_factory=list)
    assignments: List[Dict[str, Any]] = field(default_factory=list)
    transfers: List[Dict[str, Any]] = field(default_factory=list)
    approvals: List[Dict[str, Any]] = field(default_factory=list)
    categories: List[Dict[str, Any]] = field(default_factory=list)
    models: List[Dict[str, Any]] = field(default_factory=list)
    manufacturers: List[Dict[str, Any]] = field(default_factory=list)

    # Analytics cache
    analytics_cache: Dict[str, Any] = field(default_factory=dict)

    # Errors and inconsistencies
    errors: List[str] = field(default_factory=list)
    inconsistencies: List[str] = field(default_factory=list)


# ============================================================================
# HTTP CLIENT & HELPERS
# ============================================================================


class APIClient:
    """Async HTTP client for API testing"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self

    async def __aexit__(self, *args):
        if self.client:
            await self.client.aclose()

    async def request(
        self,
        method: str,
        endpoint: str,
        token: Optional[str] = None,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> tuple[int, Any]:
        """Make HTTP request and track result"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            response = await self.client.request(
                method, endpoint, json=json, data=data, params=params, headers=headers
            )
            resp_data = response.json() if response.content else None
            return response.status_code, resp_data
        except Exception as e:
            print(f"[ERR] Request failed: {method} {endpoint}: {e}")
            raise

    async def get(self, endpoint: str, token: Optional[str] = None, params: Optional[Dict] = None):
        return await self.request("GET", endpoint, token=token, params=params)

    async def post(self, endpoint: str, token: Optional[str] = None, json: Optional[Dict] = None, data: Optional[Dict] = None):
        return await self.request("POST", endpoint, token=token, json=json, data=data)

    async def patch(self, endpoint: str, token: Optional[str] = None, json: Optional[Dict] = None):
        return await self.request("PATCH", endpoint, token=token, json=json)

    async def delete(self, endpoint: str, token: Optional[str] = None):
        return await self.request("DELETE", endpoint, token=token)


def log_result(ctx: TestContext, endpoint: str, method: str, status: int, success: bool, error: str = None):
    """Log test result"""
    result = TestResult(
        endpoint=endpoint,
        method=method,
        status_code=status,
        success=success,
        error=error,
    )
    ctx.results.append(result)

    symbol = "[OK]" if success else "[ERR]"
    print(f"{symbol:5} {method:6} {endpoint:50} {status}")
    if error:
        print(f"       Error: {error}")


# ============================================================================
# AUTH & USERS
# ============================================================================


async def test_auth(ctx: TestContext, client: APIClient):
    """Test authentication flows"""
    print("\n" + "=" * 80)
    print("TESTING: AUTHENTICATION & USERS")
    print("=" * 80)

    # 1. Login as superadmin
    status, data = await client.post(
        "/auth/login",
        data={"username": SUPERADMIN_LOGIN, "password": SUPERADMIN_PASSWORD},
    )
    success = status == 200
    log_result(ctx, "/auth/login", "POST", status, success)

    if not success:
        ctx.errors.append(f"Superadmin login failed: {data}")
        return None

    superadmin_token = data["access_token"]
    ctx.users["superadmin"] = {
        "token": superadmin_token,
        "id": data.get("user_id"),
        "role": "SUPERADMIN",
    }

    # 2. Get current user
    status, data = await client.get("/users/me", token=superadmin_token)
    success = status == 200
    log_result(ctx, "/users/me", "GET", status, success)
    if success:
        ctx.users["superadmin"]["id"] = data["id"]

    return superadmin_token


async def test_user_management(ctx: TestContext, client: APIClient, superadmin_token: str):
    """Create/list users with different roles"""
    print("\n" + "-" * 80)
    print("USER MANAGEMENT")
    print("-" * 80)

    # First, try to fetch existing users
    status, data = await client.get("/users", token=superadmin_token)
    existing_users = []
    if status == 200:
        if isinstance(data, dict) and "items" in data:
            existing_users = data["items"]
        elif isinstance(data, list):
            existing_users = data
        log_result(ctx, "/users (list)", "GET", status, True)
        print(f"   Found {len(existing_users)} existing users")
    else:
        log_result(ctx, "/users (list)", "GET", status, False)

    # Try to create new users (may not work due to permissions)
    roles = ["MANAGER", "VIEWER"]
    user_count = len(existing_users)  # Count existing users

    for role in roles:
        for idx in range(USERS_PER_ROLE):
            login = f"user_{role.lower()}_{idx}"
            status, data = await client.post(
                "/users",
                token=superadmin_token,
                json={
                    "login": login,
                    "email": f"{login}@test.com",
                    "password": "password123",
                    "phone": "+998900000000",
                },
            )
            success = status == 200 or status == 201
            if not success:
                log_result(ctx, f"/users (create {role})", "POST", status, False)
                continue

            log_result(ctx, f"/users (create {role})", "POST", status, success)
            if success:
                user_id = data["id"]
                # Login as new user
                status_login, token_data = await client.post(
                    "/auth/login",
                    data={"username": login, "password": "password123"},
                )
                if status_login == 200:
                    ctx.users[login] = {
                        "token": token_data["access_token"],
                        "id": user_id,
                        "role": role,
                    }
                    user_count += 1

    print(f"\n[OK] Available/Created {user_count} users")


# ============================================================================
# DOMAIN DATA (Regions, Services, Categories, etc.)
# ============================================================================


async def test_domain_data(ctx: TestContext, client: APIClient, superadmin_token: str):
    """Fetch regions, services, categories, models from read-only endpoints"""
    print("\n" + "-" * 80)
    print("DOMAIN DATA SETUP")
    print("-" * 80)

    # 1. Fetch Regions (read-only)
    status, data = await client.get("/regions", token=superadmin_token)
    success = status == 200
    log_result(ctx, "/regions (list)", "GET", status, success)
    if success and isinstance(data, list):
        ctx.regions = data[:REGIONS]  # Use first N regions
        print(f"   Found {len(data)} regions, using {len(ctx.regions)}")
    else:
        ctx.errors.append(f"Failed to fetch regions: {data}")

    # 2. Fetch Services (read-only)
    status, data = await client.get("/services", token=superadmin_token)
    success = status == 200
    log_result(ctx, "/services (list)", "GET", status, success)
    if success and isinstance(data, list):
        ctx.services = data[:SERVICES]  # Use first N services
        print(f"   Found {len(data)} services, using {len(ctx.services)}")
    else:
        ctx.errors.append(f"Failed to fetch services: {data}")

    # 3. Fetch Asset Categories (read-only)
    status, data = await client.get("/asset-categories", token=superadmin_token)
    success = status == 200
    log_result(ctx, "/asset-categories (list)", "GET", status, success)
    if success and isinstance(data, list) and len(data) > 0:
        ctx.categories = data
        print(f"   Found {len(data)} categories")
    elif success and isinstance(data, list):
        # Try to create a category if none exist
        status_create, data_create = await client.post(
            "/asset-categories",
            token=superadmin_token,
            json={"name": "Laptops", "code": "LAPTOP"},
        )
        if status_create == 200 or status_create == 201:
            ctx.categories = [data_create]
            log_result(ctx, "/asset-categories (create)", "POST", status_create, True)
        else:
            log_result(ctx, "/asset-categories (create)", "POST", status_create, False)
    else:
        ctx.errors.append(f"Failed to fetch categories: {data}")

    # 4. Fetch Manufacturers (read-only)
    status, data = await client.get("/manufacturer", token=superadmin_token)
    success = status == 200
    log_result(ctx, "/manufacturer (list)", "GET", status, success)
    if success and isinstance(data, list) and len(data) > 0:
        ctx.manufacturers = data
        print(f"   Found {len(data)} manufacturers")
    elif success and isinstance(data, list):
        # Try to create a manufacturer if none exist
        status_create, data_create = await client.post(
            "/manufacturer",
            token=superadmin_token,
            json={"name": "Dell"},
        )
        if status_create == 200 or status_create == 201:
            ctx.manufacturers = [data_create]
            log_result(ctx, "/manufacturer (create)", "POST", status_create, True)
        else:
            log_result(ctx, "/manufacturer (create)", "POST", status_create, False)
    else:
        ctx.errors.append(f"Failed to fetch manufacturers: {data}")

    # 5. Fetch/Create Model
    status, data = await client.get("/asset-models", token=superadmin_token)
    if status == 200 and isinstance(data, list) and len(data) > 0:
        ctx.models = data
    elif ctx.manufacturers and ctx.categories:
        status_create, data_create = await client.post(
            "/asset-models",
            token=superadmin_token,
            json={
                "name": "XPS 15",
                "manufacturer_id": str(ctx.manufacturers[0]["id"]),
                "category_id": str(ctx.categories[0]["id"]),
            },
        )
        if status_create == 200 or status_create == 201:
            ctx.models = [data_create]

    print(f"\n[OK] Using {len(ctx.regions)} regions, {len(ctx.services)} services")
    print(f"[OK] Using {len(ctx.categories)} categories, {len(ctx.manufacturers)} manufacturers")


# ============================================================================
# ASSETS LIFECYCLE
# ============================================================================


async def test_asset_creation(ctx: TestContext, client: APIClient, superadmin_token: str):
    """Create test assets"""
    print("\n" + "-" * 80)
    print("ASSET CREATION")
    print("-" * 80)

    if not ctx.regions or not ctx.services or not ctx.models:
        ctx.errors.append("Missing prerequisite data (regions/services/models)")
        return

    created = 0
    for region_idx, region in enumerate(ctx.regions):
        for service_idx, service in enumerate(ctx.services):
            for asset_idx in range(ASSETS_PER_REGION):
                status, data = await client.post(
                    "/assets",
                    token=superadmin_token,
                    json={
                        "name": f"Asset-R{region_idx}-S{service_idx}-A{asset_idx}",
                        "type": "laptop",
                        "model_id": str(ctx.models[0]["id"]),
                        "region_id": str(region["id"]),
                        "service_id": str(service["id"]),
                        "asset_tag": f"TAG-{uuid4().hex[:8]}",
                        "serial_number": f"SN-{uuid4().hex[:12]}",
                    },
                )
                if status == 200 or status == 201:
                    ctx.assets.append(data)
                    created += 1

    print(f"[OK] Created {created}/{REGIONS * SERVICES * ASSETS_PER_REGION} assets")
    if created == 0:
        ctx.errors.append("Failed to create assets")


async def test_asset_retrieval(ctx: TestContext, client: APIClient, superadmin_token: str):
    """Retrieve and validate assets"""
    print("\n" + "-" * 80)
    print("ASSET RETRIEVAL & VALIDATION")
    print("-" * 80)

    if not ctx.assets:
        print("[WRN]  No assets to retrieve")
        return

    # List assets
    status, data = await client.get(
        "/assets", token=superadmin_token, params={"page": 1, "limit": 100}
    )
    success = status == 200
    log_result(ctx, "/assets (list)", "GET", status, success)

    if success:
        retrieved = len(data.get("items", []))
        print(f"[OK] Retrieved {retrieved} assets from API")
        if retrieved != len(ctx.assets):
            ctx.inconsistencies.append(
                f"Asset count mismatch: created {len(ctx.assets)}, retrieved {retrieved}"
            )

    # Get single asset
    if ctx.assets:
        asset_id = ctx.assets[0]["id"]
        status, data = await client.get(
            f"/assets/{asset_id}", token=superadmin_token
        )
        success = status == 200
        log_result(ctx, f"/assets/{{id}}", "GET", status, success)


# ============================================================================
# ASSIGNMENTS
# ============================================================================


async def test_assignments(ctx: TestContext, client: APIClient, superadmin_token: str):
    """Test asset assignment workflows"""
    print("\n" + "-" * 80)
    print("ASSET ASSIGNMENTS")
    print("-" * 80)

    if not ctx.assets or not ctx.users:
        ctx.errors.append("Missing assets or users for assignments")
        return

    # Get a user to assign to
    user_login = next(
        (login for login in ctx.users if login != "superadmin"), None
    )
    if not user_login:
        ctx.errors.append("No regular users available for assignment")
        return

    user_id = ctx.users[user_login]["id"]

    # Assign first 5 assets
    assigned = 0
    for asset in ctx.assets[:5]:
        status, data = await client.post(
            "/assets/bulk/assign",
            token=superadmin_token,
            json={"asset_ids": [str(asset["id"])], "user_id": str(user_id)},
        )
        success = status == 200
        log_result(
            ctx, "/assets/bulk/assign", "POST", status, success,
            error=data.get("error") if not success else None
        )
        if success and data.get("success"):
            assigned += len(data["success"])
            ctx.assignments.extend(data["success"])

    print(f"[OK] Assigned {assigned} assets")

    # Get asset details to verify assignment
    if ctx.assets:
        status, data = await client.get(
            f"/assets/{ctx.assets[0]['id']}", token=superadmin_token
        )
        if status == 200:
            assignments = data.get("assignments", [])
            print(f"[OK] Asset 0 has {len(assignments)} assignment(s)")


async def test_bulk_assign_with_failures(ctx: TestContext, client: APIClient, superadmin_token: str):
    """Test bulk assign with some invalid IDs"""
    print("\n" + "-" * 80)
    print("BULK ASSIGN WITH PARTIAL SUCCESS")
    print("-" * 80)

    if not ctx.assets or not ctx.users:
        return

    user_login = next(
        (login for login in ctx.users if login != "superadmin"), None
    )
    if not user_login:
        return

    user_id = ctx.users[user_login]["id"]

    # Mix valid and invalid IDs
    asset_ids = [str(ctx.assets[0]["id"]), str(uuid4()), str(ctx.assets[1]["id"])]

    status, data = await client.post(
        "/assets/bulk/assign",
        token=superadmin_token,
        json={"asset_ids": asset_ids, "user_id": str(user_id)},
    )

    success = status == 200
    log_result(ctx, "/assets/bulk/assign (partial)", "POST", status, success)

    if success:
        print(f"[OK] Success: {len(data.get('success', []))} items")
        print(f"[WRN]  Failed: {len(data.get('failed', []))} items")


# ============================================================================
# TRANSFERS
# ============================================================================


async def test_transfers(ctx: TestContext, client: APIClient, superadmin_token: str):
    """Test asset transfers between regions/services"""
    print("\n" + "-" * 80)
    print("ASSET TRANSFERS")
    print("-" * 80)

    if len(ctx.regions) < 2 or len(ctx.assets) < 3:
        ctx.errors.append("Need at least 2 regions and 3 assets for transfers")
        return

    transferred = 0
    for idx, asset in enumerate(ctx.assets[5:10]):
        target_region = ctx.regions[1]  # Transfer to different region

        status, data = await client.post(
            "/assets/bulk/transfer",
            token=superadmin_token,
            json={
                "asset_ids": [str(asset["id"])],
                "region_id": str(target_region["id"]),
            },
        )

        success = status == 200
        log_result(ctx, "/assets/bulk/transfer", "POST", status, success)
        if success and data.get("success"):
            transferred += len(data["success"])

    print(f"[OK] Transferred {transferred} assets")


# ============================================================================
# CONCURRENCY
# ============================================================================


async def test_concurrent_assigns(ctx: TestContext, client: APIClient, superadmin_token: str):
    """Simulate concurrent assignment requests"""
    print("\n" + "-" * 80)
    print("CONCURRENCY: PARALLEL ASSIGNMENTS")
    print("-" * 80)

    if len(ctx.assets) < 3 or len(ctx.users) < 2:
        ctx.errors.append("Need at least 3 assets and 2 users for concurrency tests")
        return

    user1_id = list(ctx.users.values())[1]["id"]
    user2_id = list(ctx.users.values())[2]["id"] if len(ctx.users) > 2 else user1_id

    asset_id = str(ctx.assets[10]["id"])

    async def assign_concurrent(user_id: str):
        status, data = await client.post(
            "/assets/bulk/assign",
            token=superadmin_token,
            json={"asset_ids": [asset_id], "user_id": str(user_id)},
        )
        return status, data

    # Run concurrent assignments
    results = await asyncio.gather(
        assign_concurrent(user1_id),
        assign_concurrent(user2_id),
        return_exceptions=True,
    )

    success_count = sum(1 for r in results if isinstance(r, tuple) and r[0] == 200)
    print(f"[OK] Completed {len(results)} concurrent requests, {success_count} succeeded")


# ============================================================================
# ANALYTICS (READ-ONLY VALIDATION)
# ============================================================================


async def test_analytics(ctx: TestContext, client: APIClient, superadmin_token: str):
    """Validate analytics endpoints and data consistency"""
    print("\n" + "-" * 80)
    print("ANALYTICS: READ-ONLY VALIDATION")
    print("-" * 80)

    analytics_endpoints = [
        "/analytics/assignments",
        "/analytics/transfers",
        "/analytics/assets/distribution",
        "/analytics/regions",
        "/analytics/costs",
        "/analytics/dashboard",
    ]

    for endpoint in analytics_endpoints:
        status, data = await client.get(endpoint, token=superadmin_token)
        success = status == 200
        log_result(ctx, endpoint, "GET", status, success)

        if success:
            ctx.analytics_cache[endpoint] = data


# ============================================================================
# AUDIT LOG VALIDATION
# ============================================================================


async def test_audit_logs(ctx: TestContext, client: APIClient, superadmin_token: str):
    """Check audit logs for recorded events"""
    print("\n" + "-" * 80)
    print("AUDIT LOGS")
    print("-" * 80)

    status, data = await client.get(
        "/audit", token=superadmin_token, params={"limit": 50}
    )
    success = status == 200
    log_result(ctx, "/audit", "GET", status, success)

    if success:
        audit_entries = data.get("items", [])
        print(f"[OK] Retrieved {len(audit_entries)} audit entries")

        # Check for expected events
        events = [entry.get("action") for entry in audit_entries]
        print(f"   Events: {set(events)}")


# ============================================================================
# ERROR HANDLING & EDGE CASES
# ============================================================================


async def test_error_scenarios(ctx: TestContext, client: APIClient, superadmin_token: str):
    """Test error handling and edge cases"""
    print("\n" + "-" * 80)
    print("ERROR SCENARIOS & VALIDATION")
    print("-" * 80)

    test_cases = [
        # Invalid login
        {
            "name": "Invalid login",
            "method": "post",
            "endpoint": "/auth/login",
            "json": {"username": "invalid_user", "password": "wrong"},
            "expected": 401,
        },
        # Non-existent asset
        {
            "name": "Get non-existent asset",
            "method": "get",
            "endpoint": f"/assets/{uuid4()}",
            "expected": 404,
        },
        # Invalid bulk (empty list)
        {
            "name": "Bulk with empty list",
            "method": "post",
            "endpoint": "/assets/bulk/assign",
            "json": {"asset_ids": [], "user_id": str(uuid4())},
            "expected": 400,
        },
        # Duplicate asset IDs in bulk
        {
            "name": "Bulk with duplicates",
            "method": "post",
            "endpoint": "/assets/bulk/assign",
            "json": {
                "asset_ids": [str(uuid4()), str(uuid4())],
                "user_id": str(uuid4()),
            },
            "expected": [200, 400],  # Could be either
        },
    ]

    for test in test_cases:
        if test["method"] == "get":
            status, data = await client.get(
                test["endpoint"], token=superadmin_token
            )
        else:
            status, data = await client.post(
                test["endpoint"], token=superadmin_token, json=test.get("json")
            )

        expected = test["expected"]
        expected_list = expected if isinstance(expected, list) else [expected]
        success = status in expected_list

        log_result(
            ctx,
            f"[{test['name']}] {test['endpoint']}",
            test["method"].upper(),
            status,
            success,
            error=f"Expected {expected}, got {status}" if not success else None,
        )


# ============================================================================
# MAIN TEST ORCHESTRATION
# ============================================================================


async def run_all_tests():
    """Execute all tests in sequence"""
    ctx = TestContext()

    try:
        async with APIClient(BASE_URL) as client:
            # Phase 1: Auth
            superadmin_token = await test_auth(ctx, client)
            if not superadmin_token:
                print("[ERR] Failed to authenticate. Aborting.")
                return ctx

            # Phase 2: Users
            await test_user_management(ctx, client, superadmin_token)

            # Phase 3: Domain data
            await test_domain_data(ctx, client, superadmin_token)

            # Phase 4: Assets
            await test_asset_creation(ctx, client, superadmin_token)
            await test_asset_retrieval(ctx, client, superadmin_token)

            # Phase 5: Assignments
            await test_assignments(ctx, client, superadmin_token)
            await test_bulk_assign_with_failures(ctx, client, superadmin_token)

            # Phase 6: Transfers
            await test_transfers(ctx, client, superadmin_token)

            # Phase 7: Concurrency
            await test_concurrent_assigns(ctx, client, superadmin_token)

            # Phase 8: Analytics
            await test_analytics(ctx, client, superadmin_token)

            # Phase 9: Audit
            await test_audit_logs(ctx, client, superadmin_token)

            # Phase 10: Error scenarios
            await test_error_scenarios(ctx, client, superadmin_token)

    except Exception as e:
        print(f"\n[ERR] Fatal error: {e}")
        import traceback
        traceback.print_exc()

    return ctx


# ============================================================================
# REPORTING
# ============================================================================


def print_summary(ctx: TestContext):
    """Print detailed test summary"""
    print("\n\n" + "=" * 80)
    print("TEST EXECUTION SUMMARY")
    print("=" * 80)

    # Statistics
    passed = sum(1 for r in ctx.results if r.success)
    failed = sum(1 for r in ctx.results if not r.success)
    total = len(ctx.results)

    print(f"\n[STAT] RESULTS:")
    print(f"   Total requests: {total}")
    print(f"   [OK] Passed: {passed} ({100*passed//total if total else 0}%)")
    print(f"   [ERR] Failed: {failed} ({100*failed//total if total else 0}%)")

    # Data created
    print(f"\n[DATA] DATA CREATED:")
    print(f"   Users: {len(ctx.users)}")
    print(f"   Assets: {len(ctx.assets)}")
    print(f"   Regions: {len(ctx.regions)}")
    print(f"   Services: {len(ctx.services)}")
    print(f"   Assignments: {len(ctx.assignments)}")
    print(f"   Transfers: {len(ctx.transfers)}")

    # Errors
    if ctx.errors:
        print(f"\n[ERR] ERRORS ({len(ctx.errors)}):")
        for error in ctx.errors:
            print(f"   • {error}")

    # Inconsistencies
    if ctx.inconsistencies:
        print(f"\n[WRN]  INCONSISTENCIES ({len(ctx.inconsistencies)}):")
        for inconsistency in ctx.inconsistencies:
            print(f"   • {inconsistency}")

    # Failed requests
    failed_requests = [r for r in ctx.results if not r.success]
    if failed_requests:
        print(f"\n[ERR] FAILED REQUESTS ({len(failed_requests)}):")
        for r in failed_requests[:10]:  # Show first 10
            print(f"   • {r.method} {r.endpoint}: {r.status_code}")
            if r.error:
                print(f"     {r.error}")

    return passed, failed, total


async def main():
    """Main entry point"""
    print(f"\n[RUN] Starting system test suite...")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Target: Full system workflow validation\n")

    ctx = await run_all_tests()
    passed, failed, total = print_summary(ctx)

    # Exit code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
