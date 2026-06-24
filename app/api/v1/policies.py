"""
Policies API.

GET /api/v1/policies — list every registered policy and its metadata,
so clients can discover what's available before submitting a scan.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.domain.enums import Severity
from app.policies.registry import get_all_policies

router = APIRouter(prefix="/api/v1", tags=["policies"])


class PolicyInfoResponse(BaseModel):
    policy_id: str
    name: str
    description: str
    severity: Severity


@router.get("/policies", response_model=list[PolicyInfoResponse])
def list_policies() -> list[PolicyInfoResponse]:
    infos = [policy.info() for policy in get_all_policies()]
    return [
        PolicyInfoResponse(
            policy_id=info.policy_id,
            name=info.name,
            description=info.description,
            severity=info.severity,
        )
        for info in infos
    ]
