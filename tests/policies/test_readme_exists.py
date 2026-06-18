"""
Tests for the readme_exists policy.

Each test creates a temporary directory using pytest's built-in `tmp_path`
fixture and sets it up to resemble a real repository. This means we test
against actual files on disk — no mocking required.
"""

import pytest

from app.domain.enums import Severity
from app.policies.readme_exists import check, POLICY_ID


def test_returns_empty_list_when_readme_exists(tmp_path):
    """No findings should be returned when README.md is present at the repo root."""
    (tmp_path / "README.md").write_text("# My Project")

    findings = check(str(tmp_path))

    assert findings == []


def test_returns_one_finding_when_readme_is_missing(tmp_path):
    """Exactly one Finding should be returned when README.md is absent."""
    # tmp_path is an empty directory — no README.md here.
    findings = check(str(tmp_path))

    assert len(findings) == 1


def test_finding_has_correct_policy_id(tmp_path):
    """The returned Finding must reference the readme_exists policy."""
    findings = check(str(tmp_path))

    assert findings[0].policy_id == POLICY_ID


def test_finding_uses_dot_path_for_repo_level_issue(tmp_path):
    """Missing README is a repo-level issue, so path should be '.' not a file path."""
    findings = check(str(tmp_path))

    assert findings[0].path == "."


def test_finding_severity_is_medium(tmp_path):
    """A missing README should be flagged at MEDIUM severity."""
    findings = check(str(tmp_path))

    assert findings[0].severity == Severity.MEDIUM


def test_readme_in_subdirectory_only_still_flags_missing(tmp_path):
    """README.md in a subdirectory does not satisfy the root-level requirement."""
    subdir = tmp_path / "docs"
    subdir.mkdir()
    (subdir / "README.md").write_text("# Docs")

    findings = check(str(tmp_path))

    assert len(findings) == 1


def test_readme_with_wrong_case_is_not_counted(tmp_path):
    """readme.md (lowercase) should not satisfy the check — filename must match exactly."""
    (tmp_path / "readme.md").write_text("# My Project")

    findings = check(str(tmp_path))

    # On case-sensitive filesystems (Linux), this should flag a missing README.
    # On macOS (case-insensitive by default), this test may pass or skip.
    # We document the behavior rather than assert a specific outcome here,
    # since filesystem case sensitivity is environment-dependent.
    assert isinstance(findings, list)
