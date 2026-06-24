"""
Password hashing and JWT helpers.

Uses bcrypt directly rather than passlib — passlib's bcrypt backend
detection breaks with bcrypt>=4.1 (it reads a __about__.__version__
attribute bcrypt removed), so going straight to bcrypt avoids that
entirely and drops a dependency.

JWTs use PyJWT (actively maintained, unlike python-jose) with HS256,
signed with settings.secret_key. Access tokens only — no refresh
tokens; revocation/rotation isn't justified for a first auth pass.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str:
    """
    Decode a token and return the username from its `sub` claim.

    Raises jwt.PyJWTError (expired, malformed, bad signature, etc.) —
    callers turn that into an HTTP 401 at the API boundary.
    """
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    return payload["sub"]
