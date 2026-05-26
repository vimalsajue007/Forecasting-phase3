"""
Tests for Admin module:
- Access control (admin only)
- Admin stats
- User management (list, toggle, delete)
- Dataset/forecast monitoring
"""
import pytest


@pytest.fixture(scope="module")
def admin_headers(client):
    """Register and promote an admin user, return their headers."""
    client.post("/api/auth/register", json={
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "Admin@1234",
        "full_name": "Admin User",
    })
    login = client.post("/api/auth/login", json={"username": "adminuser", "password": "Admin@1234"})
    token = login.json()["access_token"]

    # Promote to admin via DB
    from tests.conftest import TestingSessionLocal
    from app.models.user import User
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == "adminuser").first()
    if user:
        user.is_admin = True
        db.commit()
    db.close()

    return {"Authorization": f"Bearer {token}"}


class TestAdminAccess:
    def test_admin_stats_requires_admin(self, client, auth_headers):
        """Regular user cannot access admin stats."""
        res = client.get("/api/admin/stats", headers=auth_headers)
        assert res.status_code == 403

    def test_admin_stats_requires_auth(self, client):
        res = client.get("/api/admin/stats")
        assert res.status_code == 401

    def test_admin_stats_success(self, client, admin_headers):
        res = client.get("/api/admin/stats", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert "total_users" in data
        assert "total_datasets" in data
        assert "total_forecasts" in data
        assert "success_rate" in data
        assert "model_stats" in data
        assert "recent_users" in data
        assert "recent_forecasts" in data


class TestAdminUserManagement:
    def test_list_users(self, client, admin_headers):
        res = client.get("/api/admin/users", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert "users" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_list_users_with_search(self, client, admin_headers):
        res = client.get("/api/admin/users?search=testuser", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        for user in data["users"]:
            assert "testuser" in user["username"].lower() or "testuser" in user["email"].lower()

    def test_list_users_with_pagination(self, client, admin_headers):
        res = client.get("/api/admin/users?skip=0&limit=2", headers=admin_headers)
        assert res.status_code == 200
        assert len(res.json()["users"]) <= 2

    def test_toggle_user_active(self, client, admin_headers):
        # Get a non-admin user to toggle
        users_res = client.get("/api/admin/users?search=testuser", headers=admin_headers)
        users = users_res.json()["users"]
        if users:
            uid = users[0]["id"]
            original_status = users[0]["is_active"]
            res = client.patch(f"/api/admin/users/{uid}/toggle-active", headers=admin_headers)
            assert res.status_code == 200
            assert res.json()["is_active"] == (not original_status)
            # Toggle back
            client.patch(f"/api/admin/users/{uid}/toggle-active", headers=admin_headers)

    def test_cannot_deactivate_self(self, client, admin_headers):
        # Get admin user ID
        me_res = client.get("/api/auth/me", headers=admin_headers)
        uid = me_res.json()["id"]
        res = client.patch(f"/api/admin/users/{uid}/toggle-active", headers=admin_headers)
        assert res.status_code == 400

    def test_toggle_nonexistent_user(self, client, admin_headers):
        res = client.patch("/api/admin/users/999999/toggle-active", headers=admin_headers)
        assert res.status_code == 404

    def test_list_users_requires_admin(self, client, auth_headers):
        res = client.get("/api/admin/users", headers=auth_headers)
        assert res.status_code == 403


class TestAdminDatasets:
    def test_list_all_datasets(self, client, admin_headers):
        res = client.get("/api/admin/datasets", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert "datasets" in data
        assert "total" in data

    def test_list_datasets_with_search(self, client, admin_headers):
        res = client.get("/api/admin/datasets?search=Test", headers=admin_headers)
        assert res.status_code == 200

    def test_list_datasets_requires_admin(self, client, auth_headers):
        res = client.get("/api/admin/datasets", headers=auth_headers)
        assert res.status_code == 403


class TestAdminForecasts:
    def test_list_all_forecasts(self, client, admin_headers):
        res = client.get("/api/admin/forecasts", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert "forecasts" in data
        assert "total" in data

    def test_list_forecasts_filter_status(self, client, admin_headers):
        res = client.get("/api/admin/forecasts?status=completed", headers=admin_headers)
        assert res.status_code == 200

    def test_list_forecasts_requires_admin(self, client, auth_headers):
        res = client.get("/api/admin/forecasts", headers=auth_headers)
        assert res.status_code == 403
