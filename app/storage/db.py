"""
Postgres-backed scan storage.

Free functions taking a Session explicitly, rather than a singleton
store object — sessions are scoped per-request via get_db(), unlike
the old in-memory store (app/storage/memory.py, now removed) which
held state for the life of the process.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.domain.models import Finding, ScanResult
from app.storage.db_models import FindingRecord, ScanRecord


def save_scan(db: Session, result: ScanResult, owner_id: int) -> None:
    """
    Save or overwrite a scan result, keyed by its scan_id.

    owner_id is only set when creating a new record — overwriting an
    existing scan_id never reassigns ownership.
    """
    record = db.get(ScanRecord, result.scan_id)
    if record is None:
        record = ScanRecord(scan_id=result.scan_id, owner_id=owner_id)
        db.add(record)

    record.repo_path = result.repo_path
    record.status = result.status
    record.created_at = result.created_at
    record.completed_at = result.completed_at
    record.error = result.error
    record.findings = [
        FindingRecord(
            policy_id=finding.policy_id,
            path=finding.path,
            message=finding.message,
            severity=finding.severity,
            line=finding.line,
        )
        for finding in result.findings
    ]

    db.commit()


def get_scan(db: Session, scan_id: str, owner_id: int) -> Optional[ScanResult]:
    """
    Look up a scan result by id, scoped to its owner.

    Returns None both when the scan doesn't exist at all and when it
    exists but belongs to a different owner — the API layer turns
    both cases into the same 404, so a caller can't use this to probe
    whether a given scan_id exists.
    """
    record = (
        db.query(ScanRecord)
        .filter(ScanRecord.scan_id == scan_id, ScanRecord.owner_id == owner_id)
        .first()
    )
    if record is None:
        return None

    return ScanResult(
        repo_path=record.repo_path,
        scan_id=record.scan_id,
        status=record.status,
        findings=[
            Finding(
                policy_id=finding.policy_id,
                path=finding.path,
                message=finding.message,
                severity=finding.severity,
                line=finding.line,
            )
            for finding in record.findings
        ],
        created_at=record.created_at,
        completed_at=record.completed_at,
        error=record.error,
    )
