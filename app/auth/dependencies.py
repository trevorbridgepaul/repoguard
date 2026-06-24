"""
FastAPI dependency for protected routes.
"""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.storage.db_models import UserRecord
from app.storage.engine import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserRecord:
    try:
        username = decode_access_token(token)
    except jwt.PyJWTError:
        raise _CREDENTIALS_ERROR

    user = db.query(UserRecord).filter(UserRecord.username == username).first()
    if user is None:
        raise _CREDENTIALS_ERROR

    return user
