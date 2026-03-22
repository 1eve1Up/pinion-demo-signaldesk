import asyncio
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from signaldesk.db.session import dispose_engine
from signaldesk.settings import get_settings

REPO_ROOT = Path(__file__).resolve().parents[1]
API_JWT_SECRET = "api-test-jwt-secret-key-needs-sufficient-length-for-hs256"


@pytest.fixture
def auth_client(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    db_path = tmp_path / "api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("JWT_SECRET_KEY", API_JWT_SECRET)
    get_settings.cache_clear()
    asyncio.run(dispose_engine())
    command.upgrade(Config(str(REPO_ROOT / "alembic.ini")), "head")

    from signaldesk.main import app

    with TestClient(app) as client:
        yield client

    asyncio.run(dispose_engine())
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _db_isolation():
    from signaldesk.db.session import dispose_engine, reset_database_url_override

    get_settings.cache_clear()
    reset_database_url_override()
    asyncio.run(dispose_engine())
    yield
    get_settings.cache_clear()
    reset_database_url_override()
    asyncio.run(dispose_engine())
