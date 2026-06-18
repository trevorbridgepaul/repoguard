"""
Policy: README Exists

Checks that a README.md file is present at the root of the repository.
A missing README is a repo-level issue, not tied to any specific file,
so findings use path="." to indicate the repository root.
"""

import os

from app.domain.enums import Severity
from app.domain.models import Finding

POLICY_ID = "readme_exists"


def check(repo_path: str) -> list[Finding]:
    """
    Check whether README.md exists at the root of repo_path.

    Args:
        repo_path: Absolute path to the repository directory on disk.

    Returns:
        An empty list if README.md is found.
        A list with one Finding if README.md is missing.
    """
    readme_path = os.path.join(repo_path, "README.md")

    if os.path.isfile(readme_path):
        return []

    return [
        Finding(
            policy_id=POLICY_ID,
            path=".",
            message="README.md is missing from the repository root.",
            severity=Severity.MEDIUM,
        )
    ]
