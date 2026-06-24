"""
Integration tests for GET /api/v1/policies.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.policies.registry import get_all_policies

client = TestClient(app)


def test_get_policies_returns_one_entry_per_registered_policy():
    response = client.get("/api/v1/policies")

    assert response.status_code == 200
    assert len(response.json()) == len(get_all_policies())


def test_get_policies_includes_no_secrets_with_correct_metadata():
    response = client.get("/api/v1/policies")

    by_id = {entry["policy_id"]: entry for entry in response.json()}

    assert "no_secrets" in by_id
    assert by_id["no_secrets"]["severity"] == "CRITICAL"
    assert by_id["no_secrets"]["name"] == "No Secrets"


def test_get_policies_entries_have_all_expected_fields():
    response = client.get("/api/v1/policies")

    for entry in response.json():
        assert set(entry.keys()) == {"policy_id", "name", "description", "severity"}
