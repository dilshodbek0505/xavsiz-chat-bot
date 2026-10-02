import json
from datetime import UTC, datetime
from typing import Any

import aiosqlite

from safe_bot.db.database import Database
from safe_bot.domain.users import TelegramProfile, UserRecord

_COLUMNS = """
id, is_bot, first_name, last_name, username, language_code,
is_premium, added_to_attachment_menu, raw_json, created_at, updated_at
"""

_UPSERT = f"""
INSERT INTO users (
    id, is_bot, first_name, last_name, username, language_code,
    is_premium, added_to_attachment_menu, raw_json, created_at, updated_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    is_bot = excluded.is_bot,
    first_name = excluded.first_name,
    last_name = excluded.last_name,
    username = excluded.username,
    language_code = excluded.language_code,
    is_premium = excluded.is_premium,
    added_to_attachment_menu = excluded.added_to_attachment_menu,
    raw_json = excluded.raw_json,
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
                _flag(profile.is_bot),
                profile.first_name,
                profile.last_name,
                profile.username,
                profile.language_code,
                _optional_flag(profile.is_premium),
                _optional_flag(profile.added_to_attachment_menu),
                json.dumps(profile.raw, ensure_ascii=False, sort_keys=True),
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


def _flag(value: bool) -> int:
    return 1 if value else 0


def _optional_flag(value: bool | None) -> int | None:
    if value is None:
        return None
    return _flag(value)


def _optional_bool(value: int | None) -> bool | None:
    if value is None:
        return None
    return bool(value)


def _load_raw(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    loaded = json.loads(value)
    if not isinstance(loaded, dict):
        raise RuntimeError("users.raw_json obyekt bo'lishi kerak")
    return loaded


def _to_record(row: aiosqlite.Row) -> UserRecord:
    return UserRecord(
        id=row["id"],
        is_bot=bool(row["is_bot"]),
        first_name=row["first_name"],
        last_name=row["last_name"],
        username=row["username"],
        language_code=row["language_code"],
        is_premium=_optional_bool(row["is_premium"]),
        added_to_attachment_menu=_optional_bool(row["added_to_attachment_menu"]),
        raw=_load_raw(row["raw_json"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
