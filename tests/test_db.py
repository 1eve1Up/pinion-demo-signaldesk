import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from signaldesk.db.session import dispose_engine, get_engine
from signaldesk.models import User
from signaldesk.settings import get_settings

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_alembic_upgrade_head_applies(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(REPO_ROOT)
    db_path = tmp_path / "migrate.db"
    url = f"sqlite+aiosqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()

    cfg = Config(str(REPO_ROOT / "alembic.ini"))
    command.upgrade(cfg, "head")

    assert db_path.exists()


def test_user_round_trip_after_migrations(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(REPO_ROOT)
    db_path = tmp_path / "app.db"
    url = f"sqlite+aiosqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    asyncio.run(dispose_engine())

    cfg = Config(str(REPO_ROOT / "alembic.ini"))
    command.upgrade(cfg, "head")

    async def _exercise() -> None:
        engine = get_engine()
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            user = User(email="owner@example.com", hashed_password="not-plaintext")
            session.add(user)
            await session.commit()
            await session.refresh(user)
            assert user.id == 1

            result = await session.execute(
                select(User).where(User.email == "owner@example.com")
            )
            found = result.scalar_one()
            assert found.hashed_password == "not-plaintext"

    asyncio.run(_exercise())
    asyncio.run(dispose_engine())
    get_settings.cache_clear()
