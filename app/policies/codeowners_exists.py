"""
Policy: CODEOWNERS Exists

Checks that a CODEOWNERS file is present at either the repository root
or the .github/ directory. CODEOWNERS defines who is responsible for
reviewing changes to specific files or directories. Without it, pull
requests have no automatic reviewer assignments.

GitHub recognizes CODEOWNERS in two locations:
    - CODEOWNERS        (repo root)
    - .github/CODEOWNERS
"""

from pathlib import Path

from app.domain.enums import Severity
from app.domain.models import Finding

POLICY_ID = "codeowners_exists"


def check_codeowners_exists(repo_path: str) -> list[Finding]:
    """
    Check whether a CODEOWNERS file exists at the repo root or .github/.

    Args:
        repo_path: Absolute path to the repository directory on disk.

    Returns:
        An empty list if CODEOWNERS is found in either valid location.
        A list with one Finding if CODEOWNERS is missing from both locations.
    """
    root = Path(repo_path)

    if (root / "CODEOWNERS").is_file():
        return []

    if (root / ".github" / "CODEOWNERS").is_file():
        return []

    return [
        Finding(
            policy_id=POLICY_ID,
            path=".",
            message="CODEOWNERS is missing. Add it at the repo root or in .github/.",
            severity=Severity.MEDIUM,
        )
    ]
