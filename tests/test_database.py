from pathlib import Path

import aiosqlite

from safe_bot.db.database import Database

_OLD_USERS = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT,
    language_code TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


async def test_connect_adds_missing_user_columns(tmp_path: Path) -> None:
    path = tmp_path / "old.db"
    async with aiosqlite.connect(path) as connection:
        await connection.execute(_OLD_USERS)
        await connection.commit()

    database = Database(path)
    await database.connect()
    try:
        cursor = await database.connection.execute("PRAGMA table_info(users)")
        names = {row["name"] for row in await cursor.fetchall()}
    finally:
        await database.close()

    assert {
        "is_bot",
        "is_premium",
        "added_to_attachment_menu",
        "raw_json",
    } <= names
