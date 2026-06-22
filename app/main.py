"""
RepoGuard application entrypoint.

Run locally with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.api.v1.scans import router as scans_router

app = FastAPI(title="RepoGuard")
app.include_router(scans_router)
