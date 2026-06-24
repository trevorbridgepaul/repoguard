"""
Tests for the dependency_pinning policy.
"""

from app.domain.enums import Severity
from app.policies.dependency_pinning import DependencyPinningPolicy, POLICY_ID

policy = DependencyPinningPolicy()


def test_returns_empty_list_when_requirements_txt_missing(tmp_path):
    findings = policy.check(str(tmp_path))

    assert findings == []


def test_returns_empty_list_when_all_deps_pinned(tmp_path):
    (tmp_path / "requirements.txt").write_text("fastapi==0.115.0\nuvicorn==0.30.0\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_flags_unpinned_dependency(tmp_path):
    (tmp_path / "requirements.txt").write_text("fastapi\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1
    assert findings[0].policy_id == POLICY_ID


def test_finding_severity_is_high(tmp_path):
    (tmp_path / "requirements.txt").write_text("fastapi\n")

    findings = policy.check(str(tmp_path))

    assert findings[0].severity == Severity.HIGH


def test_finding_includes_correct_line_number(tmp_path):
    (tmp_path / "requirements.txt").write_text("fastapi==0.115.0\nrequests\n")

    findings = policy.check(str(tmp_path))

    assert findings[0].line == 2


def test_finding_path_is_requirements_txt(tmp_path):
    (tmp_path / "requirements.txt").write_text("requests\n")

    findings = policy.check(str(tmp_path))

    assert findings[0].path == "requirements.txt"


def test_ignores_blank_lines_and_comments(tmp_path):
    (tmp_path / "requirements.txt").write_text(
        "\n# this is a comment\nfastapi==0.115.0\n\n"
    )

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_ignores_option_lines(tmp_path):
    (tmp_path / "requirements.txt").write_text(
        "-r base.txt\n--index-url https://example.com\nfastapi==0.115.0\n"
    )

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_flags_dependency_with_range_operator_as_unpinned(tmp_path):
    (tmp_path / "requirements.txt").write_text("fastapi>=0.115.0\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1


def test_pinned_dependency_with_extras_is_not_flagged(tmp_path):
    (tmp_path / "requirements.txt").write_text("uvicorn[standard]==0.30.0\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_multiple_unpinned_dependencies_all_flagged(tmp_path):
    (tmp_path / "requirements.txt").write_text("fastapi\nrequests>=2.0\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 2
