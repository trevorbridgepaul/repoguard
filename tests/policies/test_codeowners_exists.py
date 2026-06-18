"""
Tests for the codeowners_exists policy.

Each test uses pytest's tmp_path fixture to create a real temporary directory
on disk. No mocking — the policy runs against actual files.
"""

from app.domain.enums import Severity
from app.policies.codeowners_exists import check_codeowners_exists, POLICY_ID


def test_returns_empty_list_when_codeowners_at_root(tmp_path):
    """No findings when CODEOWNERS exists at the repository root."""
    (tmp_path / "CODEOWNERS").write_text("* @owner\n")

    findings = check_codeowners_exists(str(tmp_path))

    assert findings == []


def test_returns_empty_list_when_codeowners_in_github_dir(tmp_path):
    """No findings when CODEOWNERS exists inside .github/."""
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    (github_dir / "CODEOWNERS").write_text("* @owner\n")

    findings = check_codeowners_exists(str(tmp_path))

    assert findings == []


def test_returns_one_finding_when_codeowners_is_missing(tmp_path):
    """Exactly one Finding when CODEOWNERS is absent from both valid locations."""
    findings = check_codeowners_exists(str(tmp_path))

    assert len(findings) == 1


def test_finding_has_correct_policy_id(tmp_path):
    """The returned Finding must reference the codeowners_exists policy."""
    findings = check_codeowners_exists(str(tmp_path))

    assert findings[0].policy_id == POLICY_ID


def test_finding_uses_dot_path_for_repo_level_issue(tmp_path):
    """Missing CODEOWNERS is a repo-level issue, so path should be '.'."""
    findings = check_codeowners_exists(str(tmp_path))

    assert findings[0].path == "."


def test_finding_severity_is_medium(tmp_path):
    """A missing CODEOWNERS file should be flagged at MEDIUM severity."""
    findings = check_codeowners_exists(str(tmp_path))

    assert findings[0].severity == Severity.MEDIUM


def test_codeowners_in_unrelated_subdirectory_does_not_count(tmp_path):
    """CODEOWNERS in an arbitrary subdirectory does not satisfy the check."""
    subdir = tmp_path / "docs"
    subdir.mkdir()
    (subdir / "CODEOWNERS").write_text("* @owner\n")

    findings = check_codeowners_exists(str(tmp_path))

    assert len(findings) == 1
