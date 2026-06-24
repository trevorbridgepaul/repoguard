"""
Tests for the license_header policy.
"""

from app.domain.enums import Severity
from app.policies.license_header import LicenseHeaderPolicy, POLICY_ID

policy = LicenseHeaderPolicy()


def test_returns_empty_list_when_header_present(tmp_path):
    (tmp_path / "main.py").write_text("# Copyright 2026 Acme Corp\n\nprint('hi')\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_flags_file_missing_header(tmp_path):
    (tmp_path / "main.py").write_text("def add(a, b):\n    return a + b\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1
    assert findings[0].policy_id == POLICY_ID


def test_finding_severity_is_low(tmp_path):
    (tmp_path / "main.py").write_text("def add(a, b):\n    return a + b\n")

    findings = policy.check(str(tmp_path))

    assert findings[0].severity == Severity.LOW


def test_finding_path_is_relative_to_repo(tmp_path):
    subdir = tmp_path / "src"
    subdir.mkdir()
    (subdir / "main.py").write_text("def add(a, b):\n    return a + b\n")

    findings = policy.check(str(tmp_path))

    assert findings[0].path == "src/main.py"


def test_header_outside_line_window_is_not_recognized(tmp_path):
    narrow_policy = LicenseHeaderPolicy(header_lines=2)
    lines = ["# line 1", "# line 2", "# Copyright 2026 Acme Corp", "x = 1"]
    (tmp_path / "main.py").write_text("\n".join(lines) + "\n")

    findings = narrow_policy.check(str(tmp_path))

    assert len(findings) == 1


def test_custom_header_text_via_constructor(tmp_path):
    custom_policy = LicenseHeaderPolicy(header_text="SPDX-License-Identifier")
    (tmp_path / "main.py").write_text("# SPDX-License-Identifier: MIT\n\nx = 1\n")

    findings = custom_policy.check(str(tmp_path))

    assert findings == []


def test_custom_header_lines_via_constructor(tmp_path):
    lenient_policy = LicenseHeaderPolicy(header_lines=10)
    lines = ["# line 1", "# line 2", "# Copyright 2026 Acme Corp"]
    (tmp_path / "main.py").write_text("\n".join(lines) + "\n")

    findings = lenient_policy.check(str(tmp_path))

    assert findings == []


def test_ignores_non_python_files(tmp_path):
    (tmp_path / "notes.txt").write_text("no copyright here\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_respects_gitignore(tmp_path):
    (tmp_path / ".gitignore").write_text("legacy.py\n")
    (tmp_path / "legacy.py").write_text("x = 1\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_empty_file_is_flagged(tmp_path):
    (tmp_path / "empty.py").write_text("")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1


def test_header_check_does_not_require_reading_whole_huge_file(tmp_path):
    # 10MB of body after a valid header — only the header should matter.
    body = "x = 1\n" * 2_000_000
    (tmp_path / "huge.py").write_text(f"# Copyright 2026 Acme Corp\n{body}")

    findings = policy.check(str(tmp_path))

    assert findings == []
