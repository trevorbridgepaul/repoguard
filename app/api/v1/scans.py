"""
Scans API.

POST /api/v1/scans   — submit a repo for scanning, run it synchronously,
                        store the result, and return it.
GET  /api/v1/scans/{scan_id} — poll for a previously submitted scan's result.

Synchronous execution is an intentional MVP choice (see domain/models.py
and the project plan) — no background task queue yet, so the response
to POST already reflects the finished scan.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.enums import Severity, ScanStatus
from app.domain.models import ScanRequest, ScanResult
from app.scanner.engine import run_scan
from app.storage.db import get_scan, save_scan
from app.storage.engine import get_db

router = APIRouter(prefix="/api/v1", tags=["scans"])


class ScanRequestBody(BaseModel):
    repo_path: str
    policies: Optional[list[str]] = None


class FindingResponse(BaseModel):
    policy_id: str
    path: str
    message: str
    severity: Severity
    line: Optional[int] = None


class ScanResultResponse(BaseModel):
    scan_id: str
    repo_path: str
    status: ScanStatus
    findings: list[FindingResponse]
    summary: dict[str, int]
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    @classmethod
    def from_domain(cls, result: ScanResult) -> "ScanResultResponse":
        return cls(
            scan_id=result.scan_id,
            repo_path=result.repo_path,
            status=result.status,
            findings=[
                FindingResponse(
                    policy_id=f.policy_id,
                    path=f.path,
                    message=f.message,
                    severity=f.severity,
                    line=f.line,
                )
                for f in result.findings
            ],
            summary=result.summary(),
            created_at=result.created_at,
            completed_at=result.completed_at,
            error=result.error,
        )


@router.post("/scans", response_model=ScanResultResponse, status_code=201)
def create_scan(
    body: ScanRequestBody, db: Session = Depends(get_db)
) -> ScanResultResponse:
    if not Path(body.repo_path).is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"repo_path does not exist or is not a directory: {body.repo_path}",
        )

    request = ScanRequest(repo_path=body.repo_path, policies=body.policies)
    result = run_scan(request)
    save_scan(db, result)
    return ScanResultResponse.from_domain(result)


@router.get("/scans/{scan_id}", response_model=ScanResultResponse)
def get_scan_by_id(scan_id: str, db: Session = Depends(get_db)) -> ScanResultResponse:
    result = get_scan(db, scan_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Scan not found: {scan_id}")
    return ScanResultResponse.from_domain(result)
