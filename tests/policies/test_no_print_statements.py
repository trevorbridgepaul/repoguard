"""
Tests for the no_print_statements policy.
"""

from app.domain.enums import Severity
from app.policies.no_print_statements import (
    MAX_READABLE_BYTES,
    NoPrintStatementsPolicy,
    POLICY_ID,
)

policy = NoPrintStatementsPolicy()


def test_returns_empty_list_for_clean_repo(tmp_path):
    (tmp_path / "main.py").write_text("def add(a, b):\n    return a + b\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_detects_print_statement(tmp_path):
    (tmp_path / "main.py").write_text("print('hello')\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1
    assert findings[0].policy_id == POLICY_ID


def test_detects_print_with_space_before_parens(tmp_path):
    (tmp_path / "main.py").write_text("print ('hello')\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1


def test_finding_severity_is_low(tmp_path):
    (tmp_path / "main.py").write_text("print('hello')\n")

    findings = policy.check(str(tmp_path))

    assert findings[0].severity == Severity.LOW


def test_finding_includes_correct_line_number(tmp_path):
    (tmp_path / "main.py").write_text("x = 1\ny = 2\nprint(x + y)\n")

    findings = policy.check(str(tmp_path))

    assert findings[0].line == 3


def test_finding_path_is_relative_to_repo(tmp_path):
    subdir = tmp_path / "src"
    subdir.mkdir()
    (subdir / "main.py").write_text("print('hello')\n")

    findings = policy.check(str(tmp_path))

    assert findings[0].path == "src/main.py"


def test_ignores_non_python_files(tmp_path):
    (tmp_path / "notes.txt").write_text("print('hello')\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_does_not_false_positive_on_identifier_containing_print(tmp_path):
    (tmp_path / "main.py").write_text("myprint('hello')\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_detects_multiple_print_statements_in_one_file(tmp_path):
    (tmp_path / "main.py").write_text("print('a')\nprint('b')\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 2


def test_respects_gitignore(tmp_path):
    (tmp_path / ".gitignore").write_text("legacy.py\n")
    (tmp_path / "legacy.py").write_text("print('debug')\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_skips_files_over_max_readable_bytes(tmp_path):
    padding = "x" * (MAX_READABLE_BYTES + 1)
    (tmp_path / "huge.py").write_text(f"print('hello')\n{padding}")

    findings = policy.check(str(tmp_path))

    assert findings == []
