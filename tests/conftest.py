import asyncio
from pathlib import Path

import pytest

from signaldesk.settings import get_settings

REPO_ROOT = Path(__file__).resolve().parents[1]


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
