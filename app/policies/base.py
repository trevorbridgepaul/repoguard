"""
Abstract base class for all RepoGuard policies.

Every policy — whether it checks for a file's existence, scans file
contents, or inspects directory structure — implements this same
interface. The scanner and registry only need to know about `Policy`,
never about any specific policy's internals.
"""

from abc import ABC, abstractmethod

from app.domain.models import Finding


class Policy(ABC):
    """
    A single repository check.

    Subclasses must set a `policy_id` class attribute (a unique,
    machine-readable identifier, e.g. "readme_exists") and implement
    `check`.
    """

    policy_id: str

    @abstractmethod
    def check(self, repo_path: str) -> list[Finding]:
        """
        Run this policy against a repository.

        Args:
            repo_path: Absolute path to the repository directory on disk.

        Returns:
            A list of Findings, one per violation. Empty list if the
            repository satisfies the policy.
        """
        raise NotImplementedError
