"""
Core domain models for RepoGuard.

These dataclasses define the shared vocabulary of the system.
Every other layer — the API, the scanner, the storage — imports from here.

Why dataclasses instead of Pydantic models?
  - Pydantic is a validation library designed for the API boundary (HTTP in/out).
  - Dataclasses are plain Python — no framework dependency.
  - The scanner and policy logic should not need to know about FastAPI or HTTP.
  - We can still wrap these in Pydantic response models in the API layer later.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

from app.domain.enums import Severity, ScanStatus


@dataclass
class PolicyInfo:
    """
    Describes what a policy checks — its identity and metadata.

    This is NOT the policy logic itself (that lives in app/policies/).
    This is the data representation of a policy: its name, what it does,
    and what severity violations it produces by default.

    Think of it as the "label on the box" — not the box itself.

    Fields:
        policy_id   Unique machine-readable identifier, e.g. "no_secrets".
                    Used to reference a policy in findings and API responses.
        name        Human-readable name shown in reports, e.g. "No Secrets".
        description One sentence explaining what this policy checks for.
        severity    Default severity level for violations of this policy.
                    Individual findings can override this if needed.
    """

    policy_id: str
    name: str
    description: str
    severity: Severity


@dataclass
class Finding:
    """
    A single policy violation found in a specific file.

    When the scanner runs a policy against a file and detects a problem,
    it creates a Finding. Many Findings get collected into a ScanResult.

    One Finding = one violation at one location.

    Fields:
        policy_id   Which policy produced this finding. Matches PolicyInfo.policy_id.
        path        File path where the violation was found, relative to the repo root.
                    e.g. "src/config.py" not "/Users/trevor/myrepo/src/config.py"
        message     Human-readable description of what was found.
                    e.g. "Possible AWS secret key detected on this line."
        severity    How serious this specific violation is.
        line        The line number in the file, if applicable. Optional because
                    some checks (e.g. file size) don't apply to a specific line.
    """

    policy_id: str
    path: str
    message: str
    severity: Severity
    line: Optional[int] = None  # None means the violation applies to the whole file


@dataclass
class ScanRequest:
    """
    Represents a request to scan a repository.

    This is the input to the scanning process — what the caller wants scanned
    and which policies to run. The API layer will translate an HTTP request
    body into one of these before handing it to the scanner.

    Fields:
        repo_path   Absolute path to the repository on the local filesystem.
                    e.g. "/Users/trevor/projects/myapp"
        policies    Optional list of policy IDs to run, e.g. ["no_secrets", "large_files"].
                    If None, the scanner will run all registered policies.
    """

    repo_path: str
    policies: Optional[list[str]] = None  # None = run everything


@dataclass
class ScanResult:
    """
    The complete output of a scan run.

    A ScanResult is created when a scan starts and updated as it progresses.
    When the scan finishes, it holds all Findings plus a summary.

    This is what gets stored in memory and returned by the API.

    Fields:
        scan_id       Unique identifier for this scan run. UUID4 format.
                      e.g. "3f2e1d0c-9b8a-7f6e-5d4c-3b2a1f0e9d8c"
        repo_path     The path that was scanned. Copied from ScanRequest.
        status        Current lifecycle state. Starts PENDING, ends COMPLETE or FAILED.
        findings      All violations found across all files. Empty list if none found.
        created_at    When the scan was submitted. Set once at creation, never changed.
        completed_at  When the scan finished (success or failure). None while running.
        error         If the scan failed, the error message explaining why. None otherwise.
    """

    repo_path: str
    scan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ScanStatus = ScanStatus.PENDING
    findings: list[Finding] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def summary(self) -> dict[str, int]:
        """
        Return a count of findings grouped by severity.

        Example output:
            {"LOW": 3, "MEDIUM": 1, "HIGH": 0, "CRITICAL": 2}

        Useful for a quick overview without listing every individual finding.
        Always includes all four severity levels even if count is zero,
        so callers can reliably access any key without a KeyError.
        """
        counts: dict[str, int] = {s.value: 0 for s in Severity}
        for finding in self.findings:
            counts[finding.severity.value] += 1
        return counts
