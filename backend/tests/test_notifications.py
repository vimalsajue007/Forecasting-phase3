"""
Tests for Notifications module:
- List notifications
- Unread count
- Mark single as read
- Mark all as read
- Delete notification
"""
import pytest
from app.services.notification_service import create_notification


@pytest.fixture(scope="class")
def seeded_notifications(db, registered_user):
    """Create test notifications directly via service."""
    user_id = registered_user["data"]["id"]
    for i, (title, type_) in enumerate([
        ("Forecast Done", "success"),
        ("Upload Failed", "error"),
        ("Report Ready", "info"),
    ]):
        create_notification(db, user_id, title=title, message=f"Message {i}", type=type_)
    db.commit()


class TestNotificationList:
    def test_list_notifications(self, client, auth_headers):
        res = client.get("/api/notifications/", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_list_with_limit(self, client, auth_headers):
        res = client.get("/api/notifications/?limit=2", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.json()) <= 2

    def test_list_requires_auth(self, client):
        res = client.get("/api/notifications/")
        assert res.status_code == 401


class TestUnreadCount:
    def test_unread_count(self, client, auth_headers):
        res = client.get("/api/notifications/unread-count", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "count" in data
        assert isinstance(data["count"], int)
        assert data["count"] >= 0

    def test_unread_count_requires_auth(self, client):
        res = client.get("/api/notifications/unread-count")
        assert res.status_code == 401


class TestMarkRead:
    def test_mark_all_read(self, client, auth_headers):
        res = client.patch("/api/notifications/mark-all-read", headers=auth_headers)
        assert res.status_code == 200
        # Verify count is now 0
        count_res = client.get("/api/notifications/unread-count", headers=auth_headers)
        assert count_res.json()["count"] == 0

    def test_mark_single_read(self, client, auth_headers):
        # Get first notification
        list_res = client.get("/api/notifications/", headers=auth_headers)
        notifications = list_res.json()
        if notifications:
            nid = notifications[0]["id"]
            res = client.patch(f"/api/notifications/{nid}/read", headers=auth_headers)
            assert res.status_code == 200

    def test_mark_read_requires_auth(self, client):
        res = client.patch("/api/notifications/1/read")
        assert res.status_code == 401


class TestDeleteNotification:
    def test_delete_notification(self, client, auth_headers):
        list_res = client.get("/api/notifications/", headers=auth_headers)
        notifications = list_res.json()
        if notifications:
            nid = notifications[0]["id"]
            res = client.delete(f"/api/notifications/{nid}", headers=auth_headers)
            assert res.status_code == 200

    def test_delete_requires_auth(self, client):
        res = client.delete("/api/notifications/1")
        assert res.status_code == 401
