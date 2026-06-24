"""
Policy: Dependency Pinning

Flags unpinned dependencies in requirements.txt — lines that don't pin
an exact version with `==`. Unpinned deps can resolve to a different
version on every install, which is the kind of nondeterminism that
causes "works on my machine" bugs — HIGH severity since it affects
build reproducibility for everyone who installs the repo.

If requirements.txt doesn't exist, this policy reports nothing: not
every repo manages dependencies that way (e.g. pyproject.toml-based
projects), so a missing requirements.txt isn't itself a violation.
"""

from pathlib import Path

from app.domain.enums import Severity
from app.domain.models import Finding
from app.policies.base import Policy

POLICY_ID = "dependency_pinning"


class DependencyPinningPolicy(Policy):
    policy_id = POLICY_ID
    name = "Dependency Pinning"
    description = "Flags dependencies in requirements.txt that aren't pinned to an exact version."
    severity = Severity.HIGH

    def check(self, repo_path: str) -> list[Finding]:
        requirements_path = Path(repo_path) / "requirements.txt"
        if not requirements_path.is_file():
            return []

        findings: list[Finding] = []
        lines = requirements_path.read_text(encoding="utf-8").splitlines()

        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue
            if line.startswith("-"):
                continue  # options like -r, -e, --index-url

            if "==" not in line:
                findings.append(
                    Finding(
                        policy_id=POLICY_ID,
                        path="requirements.txt",
                        message=f"Dependency '{line}' is not pinned to an exact version.",
                        severity=Severity.HIGH,
                        line=line_number,
                    )
                )

        return findings
