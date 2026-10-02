from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from safe_bot.db.database import Database
from safe_bot.db.repositories.business_connections import BusinessConnectionRepository
from safe_bot.db.repositories.users import UserRepository


@pytest.fixture
async def database(tmp_path: Path) -> AsyncIterator[Database]:
    db = Database(tmp_path / "test.db")
    await db.connect()
    try:
        yield db
    finally:
        await db.close()


@pytest.fixture
def users(database: Database) -> UserRepository:
    return UserRepository(database)


@pytest.fixture
def connections(database: Database) -> BusinessConnectionRepository:
    return BusinessConnectionRepository(database)
