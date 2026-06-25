"""
RepoGuard application entrypoint.

Run locally with: uvicorn app.main:app --reload
"""

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.auth import router as auth_router
from app.api.v1.policies import router as policies_router
from app.api.v1.scans import router as scans_router
from app.storage.engine import get_db

app = FastAPI(title="RepoGuard")
app.include_router(scans_router)
app.include_router(policies_router)
app.include_router(auth_router)


@app.get("/healthz")
def health_check(db: Session = Depends(get_db)) -> dict:
    """
    Liveness/readiness check for deploy platforms and orchestrators.

    Unversioned and at the root path (not under /api/v1) since health
    checks are infra plumbing, not part of the API surface. Actually
    queries the database rather than just returning 200 unconditionally
    — "the process is running" isn't useful if Postgres is unreachable.
    """
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unreachable")

    return {"status": "ok"}
