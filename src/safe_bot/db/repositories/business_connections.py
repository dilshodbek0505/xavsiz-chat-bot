from datetime import UTC, datetime

import aiosqlite

from safe_bot.db.database import Database
from safe_bot.domain.business import BusinessLink

_COLUMNS = """
id, user_id, user_chat_id, is_enabled,
can_delete_all_messages, can_delete_sent_messages, updated_at
"""

_UPSERT = f"""
INSERT INTO business_connections (
    id, user_id, user_chat_id, is_enabled,
    can_delete_all_messages, can_delete_sent_messages, updated_at
)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    user_id = excluded.user_id,
    user_chat_id = excluded.user_chat_id,
    is_enabled = excluded.is_enabled,
    can_delete_all_messages = excluded.can_delete_all_messages,
    can_delete_sent_messages = excluded.can_delete_sent_messages,
    updated_at = excluded.updated_at
RETURNING {_COLUMNS}
"""

_SELECT = f"SELECT {_COLUMNS} FROM business_connections WHERE id = ?"


class BusinessConnectionRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def upsert(
        self,
        *,
        connection_id: str,
        user_id: int,
        user_chat_id: int,
        is_enabled: bool,
        can_delete_all_messages: bool,
        can_delete_sent_messages: bool,
    ) -> BusinessLink:
        cursor = await self._database.connection.execute(
            _UPSERT,
            (
                connection_id,
                user_id,
                user_chat_id,
                int(is_enabled),
                int(can_delete_all_messages),
                int(can_delete_sent_messages),
                _timestamp(),
            ),
        )
        row = await cursor.fetchone()
        await self._database.connection.commit()
        if row is None:
            raise RuntimeError(f"Business ulanish saqlanmadi: {connection_id}")
        return _to_link(row)

    async def get(self, connection_id: str) -> BusinessLink | None:
        cursor = await self._database.connection.execute(_SELECT, (connection_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        return _to_link(row)


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_link(row: aiosqlite.Row) -> BusinessLink:
    return BusinessLink(
        id=row["id"],
        user_id=row["user_id"],
        user_chat_id=row["user_chat_id"],
        is_enabled=bool(row["is_enabled"]),
        can_delete_all_messages=bool(row["can_delete_all_messages"]),
        can_delete_sent_messages=bool(row["can_delete_sent_messages"]),
        updated_at=row["updated_at"],
    )
