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
"""

import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.storage.engine import engine


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
