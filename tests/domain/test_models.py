"""
Tests for domain models: Finding, ScanResult, ScanStatus, and Severity.

These tests verify that our data shapes behave correctly in isolation —
no policies, no scanner, no HTTP involved.
"""

import uuid
from datetime import timezone

import pytest

from app.domain.enums import Severity, ScanStatus
from app.domain.models import Finding, ScanResult

def test_finding_stores_all_fields():
    """A Finding created with explicit values holds exactly those values."""
    finding = Finding(
        policy_id="no_secrets",
        path="src/config.py",
        message="Possible API key detected.",
        severity=Severity.CRITICAL,
        line=42,
    )
    assert finding.policy_id == "no_secrets"
    assert finding.path == "src/config.py"
    assert finding.message == "Possible API key detected."
    assert finding.severity == Severity.CRITICAL
    assert finding.line == 42


def test_finding_line_defaults_to_none():
    """line is optional — omitting it should default to None."""
    finding = Finding(
        policy_id="readme_exists",
        path=".",
        message="README.md is missing.",
        severity=Severity.MEDIUM,
    )
    assert finding.line is None


def test_finding_path_can_be_dot_for_repo_level():
    """path='.' is the convention for repo-level findings with no specific file."""
    finding = Finding(
        policy_id="readme_exists",
        path=".",
        message="README.md is missing.",
        severity=Severity.MEDIUM,
    )
    assert finding.path == "."

def test_scan_result_default_status_is_pending():
    """A new ScanResult should start in PENDING state."""
    result = ScanResult(repo_path="/tmp/myrepo")
    assert result.status == ScanStatus.PENDING


def test_scan_result_default_findings_is_empty_list():
    """A new ScanResult should have no findings."""
    result = ScanResult(repo_path="/tmp/myrepo")
    assert result.findings == []


def test_scan_result_default_completed_at_is_none():
    """completed_at should be None until the scan finishes."""
    result = ScanResult(repo_path="/tmp/myrepo")
    assert result.completed_at is None


def test_scan_result_default_error_is_none():
    """error should be None when no failure has occurred."""
    result = ScanResult(repo_path="/tmp/myrepo")
    assert result.error is None


def test_scan_result_scan_id_is_valid_uuid():
    """scan_id should be auto-generated as a valid UUID string."""
    result = ScanResult(repo_path="/tmp/myrepo")
    # This raises ValueError if scan_id is not a valid UUID format.
    parsed = uuid.UUID(result.scan_id)
    assert str(parsed) == result.scan_id


def test_scan_result_each_instance_gets_unique_scan_id():
    """Two ScanResults created back-to-back should never share a scan_id."""
    a = ScanResult(repo_path="/tmp/repo_a")
    b = ScanResult(repo_path="/tmp/repo_b")
    assert a.scan_id != b.scan_id


def test_scan_result_created_at_is_timezone_aware():
    """created_at must carry timezone info (UTC) — not a naive datetime."""
    result = ScanResult(repo_path="/tmp/myrepo")
    assert result.created_at.tzinfo is not None
    assert result.created_at.tzinfo == timezone.utc

def test_summary_returns_all_severities_when_no_findings():
    """summary() should return all four severity keys even with an empty findings list."""
    result = ScanResult(repo_path="/tmp/myrepo")
    summary = result.summary()
    assert summary == {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}


def test_summary_counts_findings_by_severity():
    """summary() should count each Finding under its severity key."""
    result = ScanResult(repo_path="/tmp/myrepo")
    result.findings = [
        Finding(policy_id="p1", path="a.py", message="x", severity=Severity.LOW),
        Finding(policy_id="p2", path="b.py", message="y", severity=Severity.LOW),
        Finding(policy_id="p3", path="c.py", message="z", severity=Severity.CRITICAL),
    ]
    summary = result.summary()
    assert summary["LOW"] == 2
    assert summary["MEDIUM"] == 0
    assert summary["HIGH"] == 0
    assert summary["CRITICAL"] == 1


def test_summary_does_not_raise_keyerror_for_missing_severity():
    """All four severity keys must always be present, even if no findings use them."""
    result = ScanResult(repo_path="/tmp/myrepo")
    result.findings = [
        Finding(policy_id="p1", path="a.py", message="x", severity=Severity.HIGH),
    ]
    summary = result.summary()
    # These keys must exist — accessing them should not raise KeyError.
    assert "LOW" in summary
    assert "MEDIUM" in summary
    assert "HIGH" in summary
    assert "CRITICAL" in summary

def test_severity_values_exist():
    """All four Severity levels must exist with the correct string values."""
    assert Severity.LOW == "LOW"
    assert Severity.MEDIUM == "MEDIUM"
    assert Severity.HIGH == "HIGH"
    assert Severity.CRITICAL == "CRITICAL"


def test_scan_status_values_exist():
    """All four ScanStatus states must exist with the correct string values."""
    assert ScanStatus.PENDING == "PENDING"
    assert ScanStatus.RUNNING == "RUNNING"
    assert ScanStatus.COMPLETE == "COMPLETE"
    assert ScanStatus.FAILED == "FAILED"
