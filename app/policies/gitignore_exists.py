"""
Policy: .gitignore Exists

Checks that a .gitignore file is present at the root of the repository.
A missing .gitignore is a repo-level hygiene issue — without it, files like
__pycache__/, .env, or node_modules/ may be accidentally committed.
"""

from pathlib import Path

from app.domain.enums import Severity
from app.domain.models import Finding

POLICY_ID = "gitignore_exists"


def check_gitignore_exists(repo_path: str) -> list[Finding]:
    """
    Check whether .gitignore exists at the root of repo_path.

    Args:
        repo_path: Absolute path to the repository directory on disk.

    Returns:
        An empty list if .gitignore is found.
        A list with one Finding if .gitignore is missing.
    """
    gitignore_path = Path(repo_path) / ".gitignore"

    if gitignore_path.is_file():
        return []

    return [
        Finding(
            policy_id=POLICY_ID,
            path=".",
            message=".gitignore is missing from the repository root.",
            severity=Severity.LOW,
        )
    ]
