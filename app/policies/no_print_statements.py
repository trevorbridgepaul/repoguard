"""
Policy: No Print Statements

Flags print() calls left in .py files. Print statements are a common
debugging leftover that should use a logger instead — LOW severity
since it's a code-quality nit, not a correctness or security issue.
"""

import re
from pathlib import Path

from app.domain.enums import Severity
from app.domain.models import Finding
from app.policies.base import Policy
from app.scanner.file_walker import walk_files

POLICY_ID = "no_print_statements"
MAX_READABLE_BYTES = 5_000_000  # don't read huge files fully into memory

_PRINT_PATTERN = re.compile(r"\bprint\s*\(")


class NoPrintStatementsPolicy(Policy):
    policy_id = POLICY_ID
    name = "No Print Statements"
    description = "Flags print() calls left in .py files."
    severity = Severity.LOW

    def check(self, repo_path: str) -> list[Finding]:
        findings: list[Finding] = []
        root = Path(repo_path)

        for relative_path in walk_files(repo_path):
            if relative_path.suffix != ".py":
                continue

            full_path = root / relative_path
            if full_path.stat().st_size > MAX_READABLE_BYTES:
                continue  # large_files already reports oversized files

            try:
                text = full_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            for line_number, line in enumerate(text.splitlines(), start=1):
                if _PRINT_PATTERN.search(line):
                    findings.append(
                        Finding(
                            policy_id=POLICY_ID,
                            path=str(relative_path),
                            message="print() statement found; use a logger instead.",
                            severity=Severity.LOW,
                            line=line_number,
                        )
                    )

        return findings
