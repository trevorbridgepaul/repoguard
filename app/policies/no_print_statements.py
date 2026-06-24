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

_PRINT_PATTERN = re.compile(r"\bprint\s*\(")


class NoPrintStatementsPolicy(Policy):
    policy_id = POLICY_ID

    def check(self, repo_path: str) -> list[Finding]:
        findings: list[Finding] = []
        root = Path(repo_path)

        for relative_path in walk_files(repo_path):
            if relative_path.suffix != ".py":
                continue

            try:
                text = (root / relative_path).read_text(encoding="utf-8")
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
