"""
Policy: License Header

Flags .py files that don't contain a license header comment near the
top of the file. The required header text and the line window to check
are both configurable via the constructor — repos use different license
text (MIT, Apache, an internal copyright notice, etc.), so this only
checks for a configured substring rather than enforcing exact wording.
"""

from pathlib import Path

from app.domain.enums import Severity
from app.domain.models import Finding
from app.policies.base import Policy
from app.scanner.file_walker import walk_files

POLICY_ID = "license_header"
DEFAULT_HEADER_TEXT = "Copyright"
DEFAULT_HEADER_LINES = 5


class LicenseHeaderPolicy(Policy):
    policy_id = POLICY_ID
    name = "License Header"
    description = "Flags .py files missing a configured license header near the top of the file."
    severity = Severity.LOW

    def __init__(
        self,
        header_text: str = DEFAULT_HEADER_TEXT,
        header_lines: int = DEFAULT_HEADER_LINES,
    ) -> None:
        self.header_text = header_text
        self.header_lines = header_lines

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

            header = "\n".join(text.splitlines()[: self.header_lines])
            if self.header_text not in header:
                findings.append(
                    Finding(
                        policy_id=POLICY_ID,
                        path=str(relative_path),
                        message=(
                            f"Missing license header (expected "
                            f"'{self.header_text}' in the first "
                            f"{self.header_lines} lines)."
                        ),
                        severity=Severity.LOW,
                    )
                )

        return findings
