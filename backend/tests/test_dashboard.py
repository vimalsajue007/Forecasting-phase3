"""
Tests for Dashboard module:
- Stats endpoint with and without filters
- Activity feed
- Filter combinations
"""
import pytest


class TestDashboardStats:
    def test_get_stats(self, client, auth_headers):
        res = client.get("/api/dashboard/stats", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "total_datasets" in data
        assert "total_forecasts" in data
        assert "total_sales" in data
        assert "avg_accuracy" in data
        assert "monthly_trends" in data
        assert "top_products" in data
        assert "recent_forecasts" in data
        assert "model_breakdown" in data

    def test_get_stats_requires_auth(self, client):
        res = client.get("/api/dashboard/stats")
        assert res.status_code == 401

    def test_get_stats_with_date_filter(self, client, auth_headers):
        res = client.get("/api/dashboard/stats?date_from=2023-01-01&date_to=2023-12-31", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["filters_applied"]["date_from"] == "2023-01-01"
        assert data["filters_applied"]["date_to"] == "2023-12-31"

    def test_get_stats_with_category_filter(self, client, auth_headers):
        res = client.get("/api/dashboard/stats?category=ProductA", headers=auth_headers)
        assert res.status_code == 200

    def test_get_stats_with_region_filter(self, client, auth_headers):
        res = client.get("/api/dashboard/stats?region=North", headers=auth_headers)
        assert res.status_code == 200

    def test_get_stats_with_all_filters(self, client, auth_headers):
        res = client.get(
            "/api/dashboard/stats?date_from=2023-01-01&date_to=2023-12-31&category=ProductA&region=North",
            headers=auth_headers,
        )
        assert res.status_code == 200


class TestDashboardActivity:
    def test_get_activity(self, client, auth_headers):
        res = client.get("/api/dashboard/activity", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_get_activity_with_limit(self, client, auth_headers):
        res = client.get("/api/dashboard/activity?limit=5", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) <= 5

    def test_get_activity_requires_auth(self, client):
        res = client.get("/api/dashboard/activity")
        assert res.status_code == 401

    def test_activity_has_required_fields(self, client, auth_headers):
        res = client.get("/api/dashboard/activity?limit=1", headers=auth_headers)
        assert res.status_code == 200
        items = res.json()
        if items:
            item = items[0]
            assert "id" in item
            assert "name" in item
            assert "status" in item
