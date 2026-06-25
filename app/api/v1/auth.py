"""
Auth API.

POST /api/v1/auth/register — create a new user (open self-registration).
POST /api/v1/auth/login    — exchange username/password for a JWT.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, hash_password, verify_password
from app.storage.db_models import UserRecord
from app.storage.engine import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    existing = db.query(UserRecord).filter(UserRecord.username == body.username).first()
    if existing is not None:
        logger.info("registration rejected: username taken", extra={"username": body.username})
        raise HTTPException(status_code=409, detail="Username already registered")

    user = UserRecord(
        username=body.username,
        hashed_password=hash_password(body.password),
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()

    logger.info("user registered", extra={"username": user.username, "user_id": user.id})

    return UserResponse(id=user.id, username=user.username, created_at=user.created_at)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> TokenResponse:
    user = db.query(UserRecord).filter(UserRecord.username == form_data.username).first()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        # Never log the password itself, and don't distinguish "unknown
        # username" from "wrong password" here — same as the 401 response.
        logger.info("login failed", extra={"username": form_data.username})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("login succeeded", extra={"username": user.username, "user_id": user.id})

    return TokenResponse(access_token=create_access_token(user.username))
