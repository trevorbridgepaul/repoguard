"""
Integration tests for the /api/v1/scans endpoints, run through FastAPI's
TestClient against the real app and a real (transaction-rolled-back)
Postgres session — no mocking. See tests/conftest.py for db_session.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage.engine import get_db


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _make_clean_repo(tmp_path):
    (tmp_path / "README.md").write_text("# My Project")
    (tmp_path / ".gitignore").write_text("__pycache__/\n")
    (tmp_path / "CODEOWNERS").write_text("* @owner\n")
    return tmp_path


def test_post_scans_on_clean_repo_returns_complete_with_no_findings(client, tmp_path):
    _make_clean_repo(tmp_path)

    response = client.post("/api/v1/scans", json={"repo_path": str(tmp_path)})

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "COMPLETE"
    assert body["findings"] == []
    assert body["repo_path"] == str(tmp_path)


def test_post_scans_on_empty_repo_returns_one_finding_per_policy(client, tmp_path):
    response = client.post("/api/v1/scans", json={"repo_path": str(tmp_path)})

    assert response.status_code == 201
    body = response.json()
    assert len(body["findings"]) == 3
    assert body["summary"]["MEDIUM"] == 2  # readme_exists, codeowners_exists
    assert body["summary"]["LOW"] == 1  # gitignore_exists


def test_post_scans_respects_policy_subset(client, tmp_path):
    response = client.post(
        "/api/v1/scans",
        json={"repo_path": str(tmp_path), "policies": ["readme_exists"]},
    )

    assert response.status_code == 201
    body = response.json()
    assert len(body["findings"]) == 1
    assert body["findings"][0]["policy_id"] == "readme_exists"


def test_post_scans_with_nonexistent_repo_path_returns_400(client):
    response = client.post(
        "/api/v1/scans", json={"repo_path": "/not/a/real/path/anywhere"}
    )

    assert response.status_code == 400


def test_get_scan_after_post_returns_the_same_result(client, tmp_path):
    _make_clean_repo(tmp_path)
    create_response = client.post("/api/v1/scans", json={"repo_path": str(tmp_path)})
    scan_id = create_response.json()["scan_id"]

    get_response = client.get(f"/api/v1/scans/{scan_id}")

    assert get_response.status_code == 200
    assert get_response.json()["scan_id"] == scan_id


def test_get_scan_with_unknown_id_returns_404(client):
    response = client.get("/api/v1/scans/not-a-real-scan-id")

    assert response.status_code == 404
