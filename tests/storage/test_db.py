"""
Tests for Postgres-backed scan storage, against a real database (see
tests/conftest.py for the db_session/test_user fixtures — no mocking).
"""

from datetime import datetime, timezone

from app.domain.enums import ScanStatus, Severity
from app.domain.models import Finding, ScanResult
from app.storage.db import get_scan, list_scans, save_scan
from app.storage.db_models import UserRecord


def test_save_then_get_returns_equivalent_result(db_session, test_user):
    result = ScanResult(repo_path="/tmp/repo")

    save_scan(db_session, result, owner_id=test_user.id)
    fetched = get_scan(db_session, result.scan_id, owner_id=test_user.id)

    assert fetched is not None
    assert fetched.scan_id == result.scan_id
    assert fetched.repo_path == "/tmp/repo"
    assert fetched.status == ScanStatus.PENDING


def test_get_returns_none_for_unknown_scan_id(db_session, test_user):
    assert get_scan(db_session, "not-a-real-scan-id", owner_id=test_user.id) is None


def test_get_returns_none_for_a_different_owner(db_session, test_user):
    other_owner_id = test_user.id + 1
    result = ScanResult(repo_path="/tmp/repo")
    save_scan(db_session, result, owner_id=test_user.id)

    assert get_scan(db_session, result.scan_id, owner_id=other_owner_id) is None


def test_save_persists_findings(db_session, test_user):
    result = ScanResult(repo_path="/tmp/repo")
    result.findings.append(
        Finding(
            policy_id="no_secrets",
            path="a.py",
            message="Possible AWS access key detected.",
            severity=Severity.CRITICAL,
            line=3,
        )
    )

    save_scan(db_session, result, owner_id=test_user.id)
    fetched = get_scan(db_session, result.scan_id, owner_id=test_user.id)

    assert len(fetched.findings) == 1
    assert fetched.findings[0].policy_id == "no_secrets"
    assert fetched.findings[0].severity == Severity.CRITICAL
    assert fetched.findings[0].line == 3


def test_save_overwrites_existing_scan_with_same_id(db_session, test_user):
    original = ScanResult(repo_path="/tmp/repo")
    save_scan(db_session, original, owner_id=test_user.id)

    updated = ScanResult(repo_path="/tmp/repo-updated", scan_id=original.scan_id)
    save_scan(db_session, updated, owner_id=test_user.id)

    fetched = get_scan(db_session, original.scan_id, owner_id=test_user.id)

    assert fetched.repo_path == "/tmp/repo-updated"


def test_save_overwrite_replaces_findings_not_appends(db_session, test_user):
    original = ScanResult(repo_path="/tmp/repo")
    original.findings.append(
        Finding(policy_id="readme_exists", path=".", message="missing", severity=Severity.MEDIUM)
    )
    save_scan(db_session, original, owner_id=test_user.id)

    updated = ScanResult(repo_path="/tmp/repo", scan_id=original.scan_id)
    save_scan(db_session, updated, owner_id=test_user.id)

    fetched = get_scan(db_session, original.scan_id, owner_id=test_user.id)

    assert fetched.findings == []


def test_list_scans_returns_empty_list_for_user_with_no_scans(db_session, test_user):
    assert list_scans(db_session, owner_id=test_user.id) == []


def test_list_scans_returns_only_the_owners_scans(db_session, test_user):
    other_user = UserRecord(
        username="other-storage-test-user",
        hashed_password="irrelevant",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(other_user)
    db_session.flush()

    mine = ScanResult(repo_path="/tmp/mine")
    save_scan(db_session, mine, owner_id=test_user.id)
    theirs = ScanResult(repo_path="/tmp/theirs")
    save_scan(db_session, theirs, owner_id=other_user.id)

    results = list_scans(db_session, owner_id=test_user.id)

    assert [r.scan_id for r in results] == [mine.scan_id]


def test_list_scans_orders_newest_first(db_session, test_user):
    older = ScanResult(
        repo_path="/tmp/older", created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    newer = ScanResult(
        repo_path="/tmp/newer", created_at=datetime(2026, 1, 2, tzinfo=timezone.utc)
    )
    save_scan(db_session, older, owner_id=test_user.id)
    save_scan(db_session, newer, owner_id=test_user.id)

    results = list_scans(db_session, owner_id=test_user.id)

    assert [r.scan_id for r in results] == [newer.scan_id, older.scan_id]
