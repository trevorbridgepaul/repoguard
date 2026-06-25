"""
Tests for GET /healthz. No mocking — the unreachable-database case uses
a real connection attempt to a port nothing is listening on, not a
mocked driver.
"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.main import app
from app.storage.engine import get_db


def test_health_check_returns_ok_when_db_reachable(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_check_returns_503_when_db_unreachable():
    unreachable_engine = create_engine(
        "postgresql+psycopg://repoguard:repoguard@localhost:1/repoguard"
    )

    def override_get_db():
        session = Session(bind=unreachable_engine)
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get("/healthz")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
