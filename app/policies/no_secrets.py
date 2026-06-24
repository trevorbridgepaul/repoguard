"""
Policy: No Secrets

Scans every file in the repository for patterns that look like
credentials: AWS access keys, generic api_key= assignments, and PEM
private key headers. A committed secret is the most serious thing this
tool can catch, so this is the only CRITICAL-severity policy.
"""

import re
from pathlib import Path

from app.domain.enums import Severity
from app.domain.models import Finding
from app.policies.base import Policy
from app.scanner.file_walker import walk_files

POLICY_ID = "no_secrets"

_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "Possible AWS access key detected."),
    (
        re.compile(r"""api_key\s*=\s*['"][^'"]+['"]""", re.IGNORECASE),
        "Possible hardcoded API key detected.",
    ),
    (
        re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "Possible private key detected.",
    ),
]


class NoSecretsPolicy(Policy):
    policy_id = POLICY_ID
    name = "No Secrets"
    description = "Scans files for patterns that look like credentials (AWS keys, API keys, private key headers)."
    severity = Severity.CRITICAL

    def check(self, repo_path: str) -> list[Finding]:
        findings: list[Finding] = []
        root = Path(repo_path)

        for relative_path in walk_files(repo_path):
            try:
                text = (root / relative_path).read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue  # binary or unreadable file — not a text secret

            for line_number, line in enumerate(text.splitlines(), start=1):
                for pattern, message in _PATTERNS:
                    if pattern.search(line):
                        findings.append(
                            Finding(
                                policy_id=POLICY_ID,
                                path=str(relative_path),
                                message=message,
                                severity=Severity.CRITICAL,
                                line=line_number,
                            )
                        )

        return findings
