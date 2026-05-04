"""Tests for authentication and authorization."""

import uuid
from datetime import datetime, timedelta

import pytest

from auth import (
    AuthContext,
    create_access_token,
    create_refresh_token_str,
    decode_token,
    hash_password,
    require_auth,
    require_role,
    verify_password,
)
from config import settings


class TestPasswordHashing:
    def test_hash_and_verify(self):
        pw = "my_secure_password_123"
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed) is True

    def test_wrong_password_fails(self):
        pw = "correct_password"
        hashed = hash_password(pw)
        assert verify_password("wrong_password", hashed) is False

    def test_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True

    def test_same_password_different_hash(self):
        pw = "password123"
        h1 = hash_password(pw)
        h2 = hash_password(pw)
        assert h1 != h2


class TestJWT:
    def test_create_and_decode_access_token(self):
        user_id = uuid.uuid4()
        token = create_access_token(user_id, "user", False)
        decoded = decode_token(token)
        assert decoded["sub"] == str(user_id)
        assert decoded["role"] == "user"
        assert decoded["is_superuser"] is False
        assert decoded["type"] == "access"

    def test_create_and_decode_superuser_token(self):
        user_id = uuid.uuid4()
        token = create_access_token(user_id, "admin", True)
        decoded = decode_token(token)
        assert decoded["role"] == "admin"
        assert decoded["is_superuser"] is True

    def test_refresh_token(self):
        user_id = uuid.uuid4()
        token = create_refresh_token_str(user_id)
        decoded = decode_token(token)
        assert decoded["sub"] == str(user_id)
        assert decoded["type"] == "refresh"
        assert "jti" in decoded
        assert "exp" in decoded

    def test_invalid_token_returns_none(self):
        assert decode_token("not-a-real-token") is None

    def test_expired_token(self):
        old_expire = settings.jwt_access_token_expire_minutes
        settings.jwt_access_token_expire_minutes = -1
        try:
            token = create_access_token(uuid.uuid4(), "user", False)
            assert decode_token(token) is None
        finally:
            settings.jwt_access_token_expire_minutes = old_expire

    def test_tampered_token(self):
        user_id = uuid.uuid4()
        token = create_access_token(user_id, "user", False)
        tampered = token[:-5] + "XXXXX"
        assert decode_token(tampered) is None

    def test_unicode_password(self):
        pw = "héllo_wörld_密码"
        hashed = hash_password(pw)
        assert verify_password(pw, hashed) is True

    def test_very_long_password_truncated(self):
        pw = "a" * 100
        with pytest.raises(ValueError):
            hash_password(pw)


