"""
Tests for Postgres-backed scan storage, against a real database (see
tests/conftest.py for the db_session fixture — no mocking).
"""

from app.domain.enums import ScanStatus, Severity
from app.domain.models import Finding, ScanResult
from app.storage.db import get_scan, save_scan


def test_save_then_get_returns_equivalent_result(db_session):
    result = ScanResult(repo_path="/tmp/repo")

    save_scan(db_session, result)
    fetched = get_scan(db_session, result.scan_id)

    assert fetched is not None
    assert fetched.scan_id == result.scan_id
    assert fetched.repo_path == "/tmp/repo"
    assert fetched.status == ScanStatus.PENDING


def test_get_returns_none_for_unknown_scan_id(db_session):
    assert get_scan(db_session, "not-a-real-scan-id") is None


def test_save_persists_findings(db_session):
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

    save_scan(db_session, result)
    fetched = get_scan(db_session, result.scan_id)

    assert len(fetched.findings) == 1
    assert fetched.findings[0].policy_id == "no_secrets"
    assert fetched.findings[0].severity == Severity.CRITICAL
    assert fetched.findings[0].line == 3


def test_save_overwrites_existing_scan_with_same_id(db_session):
    original = ScanResult(repo_path="/tmp/repo")
    save_scan(db_session, original)

    updated = ScanResult(repo_path="/tmp/repo-updated", scan_id=original.scan_id)
    save_scan(db_session, updated)

    fetched = get_scan(db_session, original.scan_id)

    assert fetched.repo_path == "/tmp/repo-updated"


def test_save_overwrite_replaces_findings_not_appends(db_session):
    original = ScanResult(repo_path="/tmp/repo")
    original.findings.append(
        Finding(policy_id="readme_exists", path=".", message="missing", severity=Severity.MEDIUM)
    )
    save_scan(db_session, original)

    updated = ScanResult(repo_path="/tmp/repo", scan_id=original.scan_id)
    save_scan(db_session, updated)

    fetched = get_scan(db_session, original.scan_id)

    assert fetched.findings == []
