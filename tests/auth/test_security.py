"""
Tests for password hashing and JWT helpers.
"""

import time

import jwt
import pytest

from app.auth.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.core.config import settings


def test_hash_password_is_not_the_plaintext():
    hashed = hash_password("correct-password")

    assert hashed != "correct-password"


def test_verify_password_succeeds_for_correct_password():
    hashed = hash_password("correct-password")

    assert verify_password("correct-password", hashed) is True


def test_verify_password_fails_for_wrong_password():
    hashed = hash_password("correct-password")

    assert verify_password("wrong-password", hashed) is False


def test_create_and_decode_access_token_roundtrip():
    token = create_access_token("alice")

    assert decode_access_token(token) == "alice"


def test_decode_access_token_raises_for_expired_token():
    expired_payload = {"sub": "alice", "exp": time.time() - 1}
    expired_token = jwt.encode(expired_payload, settings.secret_key, algorithm="HS256")

    with pytest.raises(jwt.PyJWTError):
        decode_access_token(expired_token)


def test_decode_access_token_raises_for_garbage_token():
    with pytest.raises(jwt.PyJWTError):
        decode_access_token("not-a-real-token")
