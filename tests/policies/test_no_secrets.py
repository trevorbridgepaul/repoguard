"""
Tests for the no_secrets policy.

Each test creates real files under pytest's tmp_path fixture — no mocking.
"""

from app.domain.enums import Severity
from app.policies.no_secrets import MAX_READABLE_BYTES, NoSecretsPolicy, POLICY_ID

policy = NoSecretsPolicy()


def test_returns_empty_list_for_clean_repo(tmp_path):
    (tmp_path / "main.py").write_text("print('hello world')\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_detects_aws_access_key(tmp_path):
    (tmp_path / "config.py").write_text("AWS_KEY = 'AKIAABCDEFGHIJKLMNOP'\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1
    assert findings[0].policy_id == POLICY_ID


def test_detects_api_key_assignment(tmp_path):
    (tmp_path / "settings.py").write_text("api_key = 'sk-test-1234567890abcdef'\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1


def test_detects_pem_private_key_header(tmp_path):
    (tmp_path / "id_rsa").write_text("-----BEGIN RSA PRIVATE KEY-----\nMIIB...\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 1


def test_finding_severity_is_critical(tmp_path):
    (tmp_path / "config.py").write_text("AWS_KEY = 'AKIAABCDEFGHIJKLMNOP'\n")

    findings = policy.check(str(tmp_path))

    assert findings[0].severity == Severity.CRITICAL


def test_finding_includes_correct_line_number(tmp_path):
    (tmp_path / "config.py").write_text(
        "# line 1\n# line 2\nAWS_KEY = 'AKIAABCDEFGHIJKLMNOP'\n"
    )

    findings = policy.check(str(tmp_path))

    assert findings[0].line == 3


def test_finding_path_is_relative_to_repo(tmp_path):
    subdir = tmp_path / "src"
    subdir.mkdir()
    (subdir / "config.py").write_text("AWS_KEY = 'AKIAABCDEFGHIJKLMNOP'\n")

    findings = policy.check(str(tmp_path))

    assert findings[0].path == "src/config.py"


def test_skips_binary_files_without_crashing(tmp_path):
    (tmp_path / "image.png").write_bytes(bytes(range(256)))

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_respects_gitignore(tmp_path):
    (tmp_path / ".gitignore").write_text("secrets.txt\n")
    (tmp_path / "secrets.txt").write_text("AWS_KEY = 'AKIAABCDEFGHIJKLMNOP'\n")

    findings = policy.check(str(tmp_path))

    assert findings == []


def test_multiple_secrets_in_different_files_are_all_reported(tmp_path):
    (tmp_path / "a.py").write_text("AWS_KEY = 'AKIAABCDEFGHIJKLMNOP'\n")
    (tmp_path / "b.py").write_text("api_key = 'sk-test-1234567890abcdef'\n")

    findings = policy.check(str(tmp_path))

    assert len(findings) == 2


def test_skips_files_over_max_readable_bytes(tmp_path):
    padding = "x" * (MAX_READABLE_BYTES + 1)
    (tmp_path / "huge.py").write_text(f"AWS_KEY = 'AKIAABCDEFGHIJKLMNOP'\n{padding}")

    findings = policy.check(str(tmp_path))

    assert findings == []
