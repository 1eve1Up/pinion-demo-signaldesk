from datetime import datetime, timedelta, timezone

import jwt

from signaldesk.settings import get_settings


class MissingJwtSecretError(ValueError):
    """Raised when creating a token but JWT_SECRET_KEY is not configured."""


def create_access_token(
    subject: str,
    *,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()
    secret = settings.jwt_secret_key
    if not secret:
        raise MissingJwtSecretError(
            "JWT_SECRET_KEY must be set in the environment to sign tokens"
        )
    now = datetime.now(timezone.utc)
    delta = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    expire = now + delta
    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    secret = settings.jwt_secret_key
    if not secret:
        raise MissingJwtSecretError(
            "JWT_SECRET_KEY must be set in the environment to verify tokens"
        )
    return jwt.decode(
        token,
        secret,
        algorithms=[settings.jwt_algorithm],
    )


__all__ = [
    "MissingJwtSecretError",
    "create_access_token",
    "decode_access_token",
]
