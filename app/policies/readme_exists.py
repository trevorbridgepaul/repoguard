"""
Policy: README Exists

Checks that a README.md file is present at the root of the repository.
A missing README is a repo-level issue, not tied to any specific file,
so findings use path="." to indicate the repository root.
"""

from pathlib import Path

from app.domain.enums import Severity
from app.domain.models import Finding
from app.policies.base import Policy

POLICY_ID = "readme_exists"


class ReadmeExistsPolicy(Policy):
    policy_id = POLICY_ID

    def check(self, repo_path: str) -> list[Finding]:
        """
        Check whether README.md exists at the root of repo_path.

        Args:
            repo_path: Absolute path to the repository directory on disk.

        Returns:
            An empty list if README.md is found.
            A list with one Finding if README.md is missing.
        """
        readme_path = Path(repo_path) / "README.md"

        if readme_path.is_file():
            return []

        return [
            Finding(
                policy_id=POLICY_ID,
                path=".",
                message="README.md is missing from the repository root.",
                severity=Severity.MEDIUM,
            )
        ]
