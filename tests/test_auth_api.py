import asyncio
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from signaldesk.db.session import dispose_engine
from signaldesk.security import decode_access_token
from signaldesk.settings import get_settings

REPO_ROOT = Path(__file__).resolve().parents[1]
_API_JWT_SECRET = "api-test-jwt-secret-key-needs-sufficient-length-for-hs256"


@pytest.fixture
def auth_client(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    db_path = tmp_path / "auth_api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("JWT_SECRET_KEY", _API_JWT_SECRET)
    get_settings.cache_clear()
    asyncio.run(dispose_engine())
    command.upgrade(Config(str(REPO_ROOT / "alembic.ini")), "head")

    from signaldesk.main import app

    with TestClient(app) as client:
        yield client

    asyncio.run(dispose_engine())
    get_settings.cache_clear()


def test_register_then_login_returns_bearer_token(auth_client: TestClient) -> None:
    email = "newuser@example.com"
    password = "safe-password-xyz"
    reg = auth_client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert reg.status_code == 201
    reg_body = reg.json()
    assert reg_body["token_type"] == "bearer"
    assert reg_body["access_token"]
    payload = decode_access_token(reg_body["access_token"])
    assert payload["sub"].isdigit()

    login = auth_client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    login_body = login.json()
    assert login_body["token_type"] == "bearer"
    assert login_body["access_token"]


def test_register_duplicate_email_returns_409(auth_client: TestClient) -> None:
    body = {"email": "dup@example.com", "password": "p1"}
    r1 = auth_client.post("/auth/register", json=body)
    assert r1.status_code == 201
    r2 = auth_client.post("/auth/register", json=body)
    assert r2.status_code == 409


def test_login_wrong_password_returns_401(auth_client: TestClient) -> None:
    auth_client.post(
        "/auth/register",
        json={"email": "u@example.com", "password": "right-pass"},
    )
    bad = auth_client.post(
        "/auth/login",
        json={"email": "u@example.com", "password": "wrong-pass"},
    )
    assert bad.status_code == 401
    assert "access_token" not in bad.json()


def test_openapi_lists_auth_routes(auth_client: TestClient) -> None:
    spec = auth_client.get("/openapi.json")
    assert spec.status_code == 200
    paths = spec.json()["paths"]
    assert "/auth/register" in paths
    assert "/auth/login" in paths
