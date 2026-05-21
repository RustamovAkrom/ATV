async def test_create_role(client, superadmin_token):
    res = await client.post(
        "/rbac/roles",
        json={"name": "Admin", "slug": "admin"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert res.status_code == 200
    assert res.json()["slug"] == "admin"


async def test_duplicate_role_slug(client, superadmin_token):
    await client.post(
        "/rbac/roles",
        json={"name": "Admin", "slug": "admin"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )

    res = await client.post(
        "/rbac/roles",
        json={"name": "Admin2", "slug": "admin"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )

    assert res.status_code == 400


async def test_set_permissions(client, superadmin_token, permission_id, role_id):
    res = await client.put(
        f"/rbac/roles/{role_id}/permissions",
        json={"permission_ids": [str(permission_id)]},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )

    assert res.status_code == 200
    assert len(res.json()["permissions"]) == 1


async def test_delete_role_with_users_forbidden(
    client, superadmin_token, role_with_users
):
    res = await client.delete(
        f"/rbac/roles/{role_with_users}",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )

    assert res.status_code == 400
