from datetime import UTC, datetime

import aiosqlite

from safe_bot.db.database import Database
from safe_bot.domain.users import TelegramProfile, UserRecord

_COLUMNS = (
    "id, first_name, last_name, username, language_code, created_at, updated_at"
)

_UPSERT = f"""
INSERT INTO users (
    id, username, first_name, last_name, language_code, created_at, updated_at
)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    username = excluded.username,
    first_name = excluded.first_name,
    last_name = excluded.last_name,
    language_code = excluded.language_code,
    updated_at = excluded.updated_at
RETURNING {_COLUMNS}
"""

_SELECT = f"SELECT {_COLUMNS} FROM users WHERE id = ?"


class UserRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def upsert(self, profile: TelegramProfile) -> UserRecord:
        now = _timestamp()
        cursor = await self._database.connection.execute(
            _UPSERT,
            (
                profile.id,
                profile.username,
                profile.first_name,
                profile.last_name,
                profile.language_code,
                now,
                now,
            ),
        )
        row = await cursor.fetchone()
        await self._database.connection.commit()
        if row is None:
            raise RuntimeError(f"Foydalanuvchi saqlanmadi: {profile.id}")
        return _to_record(row)

    async def get(self, user_id: int) -> UserRecord | None:
        cursor = await self._database.connection.execute(_SELECT, (user_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        return _to_record(row)


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_record(row: aiosqlite.Row) -> UserRecord:
    return UserRecord(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        username=row["username"],
        language_code=row["language_code"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
