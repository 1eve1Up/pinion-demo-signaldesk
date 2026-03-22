from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from signaldesk.settings import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None
_bound_url: str | None = None
_url_override: str | None = None


def get_database_url() -> str:
    if _url_override is not None:
        return _url_override
    return get_settings().database_url


def set_database_url_override(url: str) -> None:
    global _url_override
    _url_override = url


def reset_database_url_override() -> None:
    global _url_override
    _url_override = None


def _configure() -> None:
    global _engine, _session_factory, _bound_url
    url = get_database_url()
    if _engine is not None and _bound_url == url:
        return
    if _engine is not None:
        raise RuntimeError("Call await dispose_engine() before changing database URL")
    _bound_url = url
    _engine = create_async_engine(url, echo=False)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def dispose_engine() -> None:
    global _engine, _session_factory, _bound_url
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None
    _bound_url = None


def get_engine() -> AsyncEngine:
    _configure()
    assert _engine is not None
    return _engine


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    _configure()
    assert _session_factory is not None
    async with _session_factory() as session:
        yield session
