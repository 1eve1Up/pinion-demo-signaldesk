from datetime import timedelta

import pytest
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from signaldesk.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from signaldesk.security.jwt_tokens import MissingJwtSecretError
from signaldesk.settings import get_settings

_TEST_JWT_SECRET = "unit-test-jwt-secret-must-be-long-enough-for-hs256"


@pytest.fixture(autouse=True)
def _jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", _TEST_JWT_SECRET)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_password_hash_and_verify_round_trip() -> None:
    raw = "correct horse battery staple"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_jwt_create_and_decode_round_trip() -> None:
    token = create_access_token("user-42")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-42"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_expired_rejected() -> None:
    token = create_access_token("u1", expires_delta=timedelta(seconds=-60))
    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token)


def test_jwt_wrong_secret_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    token = create_access_token("u1")
    monkeypatch.setenv("JWT_SECRET_KEY", "a-different-test-secret-key-not-same-as-before-xyz")
    get_settings.cache_clear()
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_jwt_malformed_rejected() -> None:
    with pytest.raises(InvalidTokenError):
        decode_access_token("not.valid.jwt")


def test_jwt_requires_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    get_settings.cache_clear()
    with pytest.raises(MissingJwtSecretError):
        create_access_token("any")
