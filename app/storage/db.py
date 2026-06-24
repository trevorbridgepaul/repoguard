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


def save_scan(db: Session, result: ScanResult) -> None:
    """Save or overwrite a scan result, keyed by its scan_id."""
    record = db.get(ScanRecord, result.scan_id)
    if record is None:
        record = ScanRecord(scan_id=result.scan_id)
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


def get_scan(db: Session, scan_id: str) -> Optional[ScanResult]:
    """Look up a scan result by id. Returns None if not found."""
    record = db.get(ScanRecord, scan_id)
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
