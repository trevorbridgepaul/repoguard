"""
Shared test fixtures.

Tests that touch storage need a real Postgres connection (schema
applied beforehand via `alembic upgrade head`) — this project tests
against real systems rather than mocking, same as the filesystem-based
policy tests.

`db_session` wraps each test in an outer transaction that's rolled back
at teardown, using SQLAlchemy's documented "join a session into an
external transaction" pattern (a SAVEPOINT that's restarted whenever
application code under test calls db.commit()) — so commits inside the
code being tested never leak into the next test.

`client` is a TestClient with get_db overridden to use that same
db_session, so requests made through it share the transaction.

`auth_headers` registers a throwaway user and logs in for a real JWT,
for tests against endpoints that require authentication.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.main import app
from app.storage.engine import engine, get_db


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "test-user", "password": "test-password"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test-user", "password": "test-password"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
