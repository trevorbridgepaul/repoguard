"""
Integration tests for the /api/v1/auth endpoints. See tests/conftest.py
for the client fixture (real app, transaction-rolled-back Postgres
session — no mocking).
"""


def test_register_returns_created_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "password": "alice-password"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert "id" in body
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_with_duplicate_username_returns_409(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "bob", "password": "bob-password"},
    )

    response = client.post(
        "/api/v1/auth/register",
        json={"username": "bob", "password": "a-different-password"},
    )

    assert response.status_code == 409


def test_login_with_correct_credentials_returns_access_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "carol", "password": "carol-password"},
    )

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "carol", "password": "carol-password"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_returns_401(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "dave", "password": "dave-password"},
    )

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "dave", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_login_with_unknown_username_returns_401(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody", "password": "whatever"},
    )

    assert response.status_code == 401
