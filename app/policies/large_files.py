"""
Policy: Large Files

Flags files over a configurable size threshold. Large files (binaries,
datasets, build artifacts accidentally committed) bloat repo size and
slow down clones — this is a MEDIUM severity hygiene check, not a
security issue.
"""

from pathlib import Path

from app.domain.enums import Severity
from app.domain.models import Finding
from app.policies.base import Policy
from app.scanner.file_walker import walk_files

POLICY_ID = "large_files"
DEFAULT_MAX_BYTES = 1_000_000  # 1 MB


class LargeFilesPolicy(Policy):
    policy_id = POLICY_ID

    def __init__(self, max_bytes: int = DEFAULT_MAX_BYTES) -> None:
        self.max_bytes = max_bytes

    def check(self, repo_path: str) -> list[Finding]:
        findings: list[Finding] = []
        root = Path(repo_path)

        for relative_path in walk_files(repo_path):
            size = (root / relative_path).stat().st_size
            if size > self.max_bytes:
                findings.append(
                    Finding(
                        policy_id=POLICY_ID,
                        path=str(relative_path),
                        message=(
                            f"File is {size:,} bytes, exceeding the "
                            f"{self.max_bytes:,} byte limit."
                        ),
                        severity=Severity.MEDIUM,
                    )
                )

        return findings
