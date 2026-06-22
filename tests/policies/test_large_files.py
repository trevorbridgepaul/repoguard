"""
Tests for the large_files policy.

Uses a small custom threshold via the constructor so tests don't need
to write real megabyte-sized files to disk.
"""

from app.domain.enums import Severity
from app.policies.large_files import LargeFilesPolicy, POLICY_ID

policy = LargeFilesPolicy(max_bytes=100)


def test_returns_empty_list_for_files_under_threshold(tmp_path):
    (tmp_path / "small.txt").write_bytes(b"x" * 50)

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_flags_file_over_threshold(tmp_path):
    (tmp_path / "big.txt").write_bytes(b"x" * 200)

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1
    assert findings[0].policy_id == POLICY_ID


def test_does_not_flag_file_exactly_at_threshold(tmp_path):
    (tmp_path / "exact.txt").write_bytes(b"x" * 100)

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_flags_file_one_byte_over_threshold(tmp_path):
    (tmp_path / "over.txt").write_bytes(b"x" * 101)

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1


def test_finding_severity_is_medium(tmp_path):
    (tmp_path / "big.txt").write_bytes(b"x" * 200)

    findings = policy.check(str(tmp_path))

    assert findings[0].severity == Severity.MEDIUM


def test_finding_path_is_relative_to_repo(tmp_path):
    subdir = tmp_path / "assets"
    subdir.mkdir()
    (subdir / "big.bin").write_bytes(b"x" * 200)

    findings = policy.check(str(tmp_path))

    assert findings[0].path == "assets/big.bin"


def test_respects_gitignore(tmp_path):
    (tmp_path / ".gitignore").write_text("big.bin\n")
    (tmp_path / "big.bin").write_bytes(b"x" * 200)

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_custom_threshold_via_constructor(tmp_path):
    lenient_policy = LargeFilesPolicy(max_bytes=1000)
    (tmp_path / "medium.txt").write_bytes(b"x" * 200)

    findings = lenient_policy.check(str(tmp_path))

    assert findings == []


def test_default_threshold_is_one_megabyte():
    default_policy = LargeFilesPolicy()

    assert default_policy.max_bytes == 1_000_000
