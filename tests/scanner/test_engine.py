"""
Tests for the scanner engine.

Each test runs against a real temporary directory via pytest's tmp_path
fixture, exercising the real registered policies — no mocking.
"""

from app.domain.enums import ScanStatus
from app.domain.models import ScanRequest
from app.scanner.engine import run_scan


def _make_clean_repo(tmp_path):
    """A repo that satisfies every currently registered policy."""
    (tmp_path / "README.md").write_text("# My Project")
    (tmp_path / ".gitignore").write_text("__pycache__/\n")
    (tmp_path / "CODEOWNERS").write_text("* @owner\n")
    return tmp_path


def test_clean_repo_completes_with_no_findings(tmp_path):
    _make_clean_repo(tmp_path)

    result = run_scan(ScanRequest(repo_path=str(tmp_path)))

    assert result.status == ScanStatus.COMPLETE
    assert result.findings == []


def test_empty_repo_collects_one_finding_per_repo_hygiene_policy(tmp_path):
    # tmp_path is empty — every repo-hygiene policy should fire exactly once.
    # no_secrets has no files to scan, so it contributes nothing here.
    result = run_scan(ScanRequest(repo_path=str(tmp_path)))

    assert result.status == ScanStatus.COMPLETE
    policy_ids = {f.policy_id for f in result.findings}
    assert policy_ids == {"readme_exists", "gitignore_exists", "codeowners_exists"}
    assert len(result.findings) == 3


def test_policy_subset_only_runs_requested_policies(tmp_path):
    request = ScanRequest(repo_path=str(tmp_path), policies=["readme_exists"])

    result = run_scan(request)

    assert result.status == ScanStatus.COMPLETE
    assert len(result.findings) == 1
    assert result.findings[0].policy_id == "readme_exists"


def test_result_carries_repo_path_and_completed_at(tmp_path):
    _make_clean_repo(tmp_path)

    result = run_scan(ScanRequest(repo_path=str(tmp_path)))

    assert result.repo_path == str(tmp_path)
    assert result.completed_at is not None


def test_unknown_policy_id_marks_scan_failed(tmp_path):
    request = ScanRequest(repo_path=str(tmp_path), policies=["not_a_real_policy"])

    result = run_scan(request)

    assert result.status == ScanStatus.FAILED
    assert result.error is not None
    assert result.completed_at is not None
