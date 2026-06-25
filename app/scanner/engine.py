"""
Scanner engine.

Orchestrates a scan: resolves which policies to run from the registry,
runs each one against the repo, and collects the results into a
ScanResult. This is the only place that ties policies together into a
single scan run — the API layer and storage layer build on top of it.
"""

import logging
import time
from datetime import datetime, timezone

from app.domain.enums import ScanStatus
from app.domain.models import ScanRequest, ScanResult
from app.policies.registry import get_policies

logger = logging.getLogger(__name__)


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
    started = time.monotonic()

    logger.info(
        "scan started",
        extra={"scan_id": result.scan_id, "repo_path": request.repo_path},
    )

    try:
        for policy in get_policies(request.policies):
            result.findings.extend(policy.check(request.repo_path))
        result.status = ScanStatus.COMPLETE
    except Exception as exc:
        result.status = ScanStatus.FAILED
        result.error = str(exc)

    result.completed_at = datetime.now(timezone.utc)

    duration_ms = round((time.monotonic() - started) * 1000, 1)
    log = logger.info if result.status == ScanStatus.COMPLETE else logger.warning
    log(
        "scan finished",
        extra={
            "scan_id": result.scan_id,
            "status": result.status.value,
            "finding_count": len(result.findings),
            "duration_ms": duration_ms,
        },
    )

    return result
