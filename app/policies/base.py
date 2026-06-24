"""
Abstract base class for all RepoGuard policies.

Every policy — whether it checks for a file's existence, scans file
contents, or inspects directory structure — implements this same
interface. The scanner and registry only need to know about `Policy`,
never about any specific policy's internals.
"""

from abc import ABC, abstractmethod

from app.domain.enums import Severity
from app.domain.models import Finding, PolicyInfo


class Policy(ABC):
    """
    A single repository check.

    Subclasses must set `policy_id`, `name`, `description`, and
    `severity` class attributes — these describe the policy and back
    `info()` and the `GET /policies` endpoint — and implement `check`.
    """

    policy_id: str
    name: str
    description: str
    severity: Severity

    def info(self) -> PolicyInfo:
        return PolicyInfo(
            policy_id=self.policy_id,
            name=self.name,
            description=self.description,
            severity=self.severity,
        )

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
