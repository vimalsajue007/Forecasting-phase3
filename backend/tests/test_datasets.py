"""
Tests for Dataset module:
- Upload CSV/Excel
- List datasets with pagination/search/filter
- Get single dataset
- Preview dataset
- Delete dataset
- Validation and error handling
"""
import pytest
import io
import csv


def make_csv_bytes(rows=20):
    """Generate a valid in-memory CSV file."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["date", "sales", "product", "region"])
    for i in range(rows):
        writer.writerow([f"2023-{(i%12)+1:02d}-01", 1000 + i * 50, f"Product{i%3}", ["North","South","East"][i%3]])
    return buf.getvalue().encode()


class TestDatasetUpload:
    def test_upload_csv_success(self, client, auth_headers):
        csv_data = make_csv_bytes()
        res = client.post(
            "/api/datasets/upload",
            files={"file": ("test.csv", io.BytesIO(csv_data), "text/csv")},
            data={"name": "Test Dataset"},
            headers=auth_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == "Test Dataset"
        assert data["filename"] == "test.csv"
        assert data["status"] in ("processed", "uploaded")

    def test_upload_unsupported_format(self, client, auth_headers):
        res = client.post(
            "/api/datasets/upload",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
            data={"name": "Bad File"},
            headers=auth_headers,
        )
        assert res.status_code == 400

    def test_upload_requires_auth(self, client):
        csv_data = make_csv_bytes()
        res = client.post(
            "/api/datasets/upload",
            files={"file": ("test.csv", io.BytesIO(csv_data), "text/csv")},
            data={"name": "Test"},
        )
        assert res.status_code == 401

    def test_upload_missing_name(self, client, auth_headers):
        csv_data = make_csv_bytes()
        res = client.post(
            "/api/datasets/upload",
            files={"file": ("test.csv", io.BytesIO(csv_data), "text/csv")},
            headers=auth_headers,
        )
        assert res.status_code == 422


class TestDatasetList:
    def test_list_datasets(self, client, auth_headers):
        res = client.get("/api/datasets/", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "datasets" in data or isinstance(data, list)

    def test_list_with_pagination(self, client, auth_headers):
        res = client.get("/api/datasets/?skip=0&limit=5", headers=auth_headers)
        assert res.status_code == 200

    def test_list_with_search(self, client, auth_headers):
        res = client.get("/api/datasets/?search=Test", headers=auth_headers)
        assert res.status_code == 200

    def test_list_with_status_filter(self, client, auth_headers):
        res = client.get("/api/datasets/?status=processed", headers=auth_headers)
        assert res.status_code == 200

    def test_list_requires_auth(self, client):
        res = client.get("/api/datasets/")
        assert res.status_code == 401


class TestDatasetOperations:
    @pytest.fixture(scope="class")
    def uploaded_dataset(self, client, auth_headers):
        csv_data = make_csv_bytes()
        res = client.post(
            "/api/datasets/upload",
            files={"file": ("ops_test.csv", io.BytesIO(csv_data), "text/csv")},
            data={"name": "Ops Test Dataset"},
            headers=auth_headers,
        )
        assert res.status_code == 200
        return res.json()

    def test_get_dataset_by_id(self, client, auth_headers, uploaded_dataset):
        ds_id = uploaded_dataset["id"]
        res = client.get(f"/api/datasets/{ds_id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["id"] == ds_id

    def test_get_nonexistent_dataset(self, client, auth_headers):
        res = client.get("/api/datasets/999999", headers=auth_headers)
        assert res.status_code == 404

    def test_preview_dataset(self, client, auth_headers, uploaded_dataset):
        ds_id = uploaded_dataset["id"]
        res = client.get(f"/api/datasets/{ds_id}/preview", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "columns" in data
        assert "preview" in data
        assert "shape" in data

    def test_delete_dataset(self, client, auth_headers):
        csv_data = make_csv_bytes()
        upload = client.post(
            "/api/datasets/upload",
            files={"file": ("delete_me.csv", io.BytesIO(csv_data), "text/csv")},
            data={"name": "To Delete"},
            headers=auth_headers,
        )
        ds_id = upload.json()["id"]
        res = client.delete(f"/api/datasets/{ds_id}", headers=auth_headers)
        assert res.status_code == 200
        # Verify it's gone
        res2 = client.get(f"/api/datasets/{ds_id}", headers=auth_headers)
        assert res2.status_code == 404

    def test_cannot_access_other_users_dataset(self, client):
        # Register second user
        client.post("/api/auth/register", json={
            "username": "user2", "email": "user2@example.com", "password": "Pass@1234"
        })
        login = client.post("/api/auth/login", json={"username": "user2", "password": "Pass@1234"})
        token2 = login.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        # Try to access dataset 1 (belongs to testuser)
        res = client.get("/api/datasets/1", headers=headers2)
        assert res.status_code == 404
