"""
Tests for Authentication module:
- Register
- Login
- Get current user
- Update profile
- Change password
- Token endpoint (Swagger)
"""
import pytest


class TestRegister:
    def test_register_success(self, client):
        res = client.post("/api/auth/register", json={
            "username": "newuser1",
            "email": "newuser1@example.com",
            "password": "Pass@1234",
            "full_name": "New User",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["username"] == "newuser1"
        assert data["email"] == "newuser1@example.com"
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client, registered_user):
        res = client.post("/api/auth/register", json={
            "username": registered_user["username"],
            "email": "unique@example.com",
            "password": "Pass@1234",
        })
        assert res.status_code == 400
        assert "username" in res.json()["detail"].lower()

    def test_register_duplicate_email(self, client, registered_user):
        res = client.post("/api/auth/register", json={
            "username": "uniqueuser",
            "email": registered_user["data"]["email"],
            "password": "Pass@1234",
        })
        assert res.status_code == 400
        assert "email" in res.json()["detail"].lower()

    def test_register_missing_fields(self, client):
        res = client.post("/api/auth/register", json={"username": "onlyname"})
        assert res.status_code == 422

    def test_register_invalid_email(self, client):
        res = client.post("/api/auth/register", json={
            "username": "badmail",
            "email": "not-an-email",
            "password": "Pass@1234",
        })
        assert res.status_code == 422


class TestLogin:
    def test_login_success(self, client, registered_user):
        res = client.post("/api/auth/login", json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == registered_user["username"]

    def test_login_wrong_password(self, client, registered_user):
        res = client.post("/api/auth/login", json={
            "username": registered_user["username"],
            "password": "wrongpassword",
        })
        assert res.status_code == 401

    def test_login_wrong_username(self, client):
        res = client.post("/api/auth/login", json={
            "username": "doesnotexist",
            "password": "anypassword",
        })
        assert res.status_code == 401

    def test_login_missing_fields(self, client):
        res = client.post("/api/auth/login", json={"username": "testuser"})
        assert res.status_code == 422

    def test_token_endpoint_swagger(self, client, registered_user):
        """Test OAuth2 form-based token endpoint for Swagger UI."""
        res = client.post("/api/auth/token", data={
            "grant_type": "password",
            "username": registered_user["username"],
            "password": registered_user["password"],
        })
        assert res.status_code == 200
        assert "access_token" in res.json()


class TestProtectedEndpoints:
    def test_get_me_authenticated(self, client, auth_headers, registered_user):
        res = client.get("/api/auth/me", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["username"] == registered_user["username"]

    def test_get_me_unauthenticated(self, client):
        res = client.get("/api/auth/me")
        assert res.status_code == 401

    def test_get_me_invalid_token(self, client):
        res = client.get("/api/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert res.status_code == 401

    def test_update_profile(self, client, auth_headers):
        res = client.patch("/api/auth/me", json={"full_name": "Updated Name"}, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["full_name"] == "Updated Name"

    def test_change_password_wrong_current(self, client, auth_headers):
        res = client.post("/api/auth/change-password", json={
            "current_password": "wrongpassword",
            "new_password": "NewPass@1234",
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_change_password_too_short(self, client, auth_headers):
        res = client.post("/api/auth/change-password", json={
            "current_password": "Test@1234",
            "new_password": "abc",
        }, headers=auth_headers)
        assert res.status_code == 400
