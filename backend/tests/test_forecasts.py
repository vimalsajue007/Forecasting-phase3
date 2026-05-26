"""
Tests for Forecasting module:
- Create forecast
- List with pagination/search/filter
- Get forecast by ID
- Delete forecast
- Get supported models
- Model comparison
- Validation
"""
import pytest
import io
import csv
import time


def make_csv_bytes(rows=30):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["date", "sales", "product", "region"])
    for i in range(rows):
        writer.writerow([f"2023-{(i%12)+1:02d}-{(i%28)+1:02d}", 500 + i * 30, f"Prod{i%3}", "North"])
    return buf.getvalue().encode()


@pytest.fixture(scope="module")
def processed_dataset(client, auth_headers):
    """Upload and return a processed dataset for forecast tests."""
    csv_data = make_csv_bytes(30)
    res = client.post(
        "/api/datasets/upload",
        files={"file": ("forecast_data.csv", io.BytesIO(csv_data), "text/csv")},
        data={"name": "Forecast Test Data"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    return res.json()


class TestForecastModels:
    def test_get_supported_models(self, client, auth_headers):
        res = client.get("/api/forecasts/models", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "models" in data
        model_values = [m["value"] for m in data["models"]]
        assert "linear_regression" in model_values
        assert "ridge_regression" in model_values
        assert "random_forest" in model_values
        assert "gradient_boosting" in model_values

    def test_get_models_requires_auth(self, client):
        res = client.get("/api/forecasts/models")
        assert res.status_code == 401


class TestForecastCreate:
    def test_create_linear_regression(self, client, auth_headers, processed_dataset):
        res = client.post("/api/forecasts/", json={
            "name": "LR Test",
            "dataset_id": processed_dataset["id"],
            "model_type": "linear_regression",
            "periods": 6,
            "target_column": "sales",
            "date_column": "date",
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "LR Test"
        assert data["status"] in ("running", "completed", "pending")

    def test_create_ridge_regression(self, client, auth_headers, processed_dataset):
        res = client.post("/api/forecasts/", json={
            "name": "Ridge Test",
            "dataset_id": processed_dataset["id"],
            "model_type": "ridge_regression",
            "periods": 6,
            "target_column": "sales",
            "date_column": "date",
        }, headers=auth_headers)
        assert res.status_code == 201

    def test_create_random_forest(self, client, auth_headers, processed_dataset):
        res = client.post("/api/forecasts/", json={
            "name": "RF Test",
            "dataset_id": processed_dataset["id"],
            "model_type": "random_forest",
            "periods": 6,
            "target_column": "sales",
            "date_column": "date",
        }, headers=auth_headers)
        assert res.status_code == 201

    def test_create_gradient_boosting(self, client, auth_headers, processed_dataset):
        res = client.post("/api/forecasts/", json={
            "name": "GB Test",
            "dataset_id": processed_dataset["id"],
            "model_type": "gradient_boosting",
            "periods": 6,
            "target_column": "sales",
            "date_column": "date",
        }, headers=auth_headers)
        assert res.status_code == 201

    def test_create_invalid_model(self, client, auth_headers, processed_dataset):
        res = client.post("/api/forecasts/", json={
            "name": "Bad Model",
            "dataset_id": processed_dataset["id"],
            "model_type": "invalid_model_xyz",
            "periods": 6,
            "target_column": "sales",
            "date_column": "date",
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_create_missing_dataset(self, client, auth_headers):
        res = client.post("/api/forecasts/", json={
            "name": "No Dataset",
            "dataset_id": 999999,
            "model_type": "linear_regression",
            "periods": 6,
            "target_column": "sales",
            "date_column": "date",
        }, headers=auth_headers)
        assert res.status_code == 404

    def test_create_missing_required_fields(self, client, auth_headers, processed_dataset):
        res = client.post("/api/forecasts/", json={
            "name": "Missing columns",
            "dataset_id": processed_dataset["id"],
            "model_type": "linear_regression",
            "periods": 6,
        }, headers=auth_headers)
        assert res.status_code == 422

    def test_create_requires_auth(self, client, processed_dataset):
        res = client.post("/api/forecasts/", json={
            "name": "No Auth",
            "dataset_id": processed_dataset["id"],
            "model_type": "linear_regression",
            "periods": 6,
            "target_column": "sales",
            "date_column": "date",
        })
        assert res.status_code == 401


class TestForecastList:
    def test_list_forecasts(self, client, auth_headers):
        res = client.get("/api/forecasts/", headers=auth_headers)
        assert res.status_code == 200

    def test_list_with_pagination(self, client, auth_headers):
        res = client.get("/api/forecasts/?skip=0&limit=5", headers=auth_headers)
        assert res.status_code == 200

    def test_list_filter_by_status(self, client, auth_headers):
        res = client.get("/api/forecasts/?status=running", headers=auth_headers)
        assert res.status_code == 200

    def test_list_search_by_name(self, client, auth_headers):
        res = client.get("/api/forecasts/?search=LR", headers=auth_headers)
        assert res.status_code == 200

    def test_list_filter_by_model(self, client, auth_headers):
        res = client.get("/api/forecasts/?model_type=linear_regression", headers=auth_headers)
        assert res.status_code == 200

    def test_list_requires_auth(self, client):
        res = client.get("/api/forecasts/")
        assert res.status_code == 401


class TestForecastGet:
    def test_get_forecast_by_id(self, client, auth_headers, processed_dataset):
        create = client.post("/api/forecasts/", json={
            "name": "Get Test",
            "dataset_id": processed_dataset["id"],
            "model_type": "linear_regression",
            "periods": 3,
            "target_column": "sales",
            "date_column": "date",
        }, headers=auth_headers)
        fid = create.json()["id"]
        res = client.get(f"/api/forecasts/{fid}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["id"] == fid

    def test_get_nonexistent_forecast(self, client, auth_headers):
        res = client.get("/api/forecasts/999999", headers=auth_headers)
        assert res.status_code == 404


class TestForecastDelete:
    def test_delete_forecast(self, client, auth_headers, processed_dataset):
        create = client.post("/api/forecasts/", json={
            "name": "Delete Me",
            "dataset_id": processed_dataset["id"],
            "model_type": "linear_regression",
            "periods": 3,
            "target_column": "sales",
            "date_column": "date",
        }, headers=auth_headers)
        fid = create.json()["id"]
        res = client.delete(f"/api/forecasts/{fid}", headers=auth_headers)
        assert res.status_code == 200
        res2 = client.get(f"/api/forecasts/{fid}", headers=auth_headers)
        assert res2.status_code == 404

    def test_delete_nonexistent_forecast(self, client, auth_headers):
        res = client.delete("/api/forecasts/999999", headers=auth_headers)
        assert res.status_code == 404


class TestModelComparison:
    def test_compare_models(self, client, auth_headers, processed_dataset):
        res = client.post(
            "/api/forecasts/compare",
            params={
                "dataset_id": processed_dataset["id"],
                "target_column": "sales",
                "date_column": "date",
                "periods": 6,
            },
            headers=auth_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert "results" in data
        assert "best_model" in data
        assert len(data["results"]) > 0

    def test_compare_invalid_dataset(self, client, auth_headers):
        res = client.post(
            "/api/forecasts/compare",
            params={
                "dataset_id": 999999,
                "target_column": "sales",
                "date_column": "date",
                "periods": 6,
            },
            headers=auth_headers,
        )
        assert res.status_code == 404
