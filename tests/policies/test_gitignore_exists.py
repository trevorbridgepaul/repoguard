"""
Tests for the gitignore_exists policy.

Each test uses pytest's tmp_path fixture to create a real temporary directory
on disk. No mocking — the policy runs against actual files.
"""

from app.domain.enums import Severity
from app.policies.gitignore_exists import GitignoreExistsPolicy, POLICY_ID

policy = GitignoreExistsPolicy()


def test_returns_empty_list_when_gitignore_exists(tmp_path):
    """No findings should be returned when .gitignore is present at the repo root."""
    (tmp_path / ".gitignore").write_text("__pycache__/\n.env\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_returns_one_finding_when_gitignore_is_missing(tmp_path):
    """Exactly one Finding should be returned when .gitignore is absent."""
    findings = policy.check(str(tmp_path))

    assert len(findings) == 1


def test_finding_has_correct_policy_id(tmp_path):
    """The returned Finding must reference the gitignore_exists policy."""
    findings = policy.check(str(tmp_path))

    assert findings[0].policy_id == POLICY_ID


def test_finding_uses_dot_path_for_repo_level_issue(tmp_path):
    """Missing .gitignore is a repo-level issue, so path should be '.' not a file path."""
    findings = policy.check(str(tmp_path))

    assert findings[0].path == "."


def test_finding_severity_is_low(tmp_path):
    """A missing .gitignore should be flagged at LOW severity."""
    findings = policy.check(str(tmp_path))

    assert findings[0].severity == Severity.LOW


def test_gitignore_in_subdirectory_only_still_flags_missing(tmp_path):
    """.gitignore in a subdirectory does not satisfy the root-level requirement."""
    subdir = tmp_path / "config"
    subdir.mkdir()
    (subdir / ".gitignore").write_text("*.log\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1
