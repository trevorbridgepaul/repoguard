"""
Scanner engine.

Orchestrates a scan: resolves which policies to run from the registry,
runs each one against the repo, and collects the results into a
ScanResult. This is the only place that ties policies together into a
single scan run — the API layer and storage layer build on top of it.
"""

from datetime import datetime, timezone

from app.domain.enums import ScanStatus
from app.domain.models import ScanRequest, ScanResult
from app.policies.registry import get_policies


def run_scan(request: ScanRequest) -> ScanResult:
    """
    Run a scan for the given request and return the completed ScanResult.

    If a policy_id in the request is unknown, or a policy raises while
    checking, the scan is marked FAILED with the error recorded rather
    than letting the exception propagate — ScanResult.error exists for
    exactly this case, since callers poll for results rather than
    catching exceptions directly.
    """
    result = ScanResult(repo_path=request.repo_path, status=ScanStatus.RUNNING)

    try:
        for policy in get_policies(request.policies):
            result.findings.extend(policy.check(request.repo_path))
        result.status = ScanStatus.COMPLETE
    except Exception as exc:
        result.status = ScanStatus.FAILED
        result.error = str(exc)

    result.completed_at = datetime.now(timezone.utc)
    return result
