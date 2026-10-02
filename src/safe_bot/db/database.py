from pathlib import Path

import aiosqlite

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

# Eski bazalarga yangi ustunlar. CREATE TABLE IF NOT EXISTS mavjud jadvalni o'zgartirmaydi.
_USER_COLUMN_ADDITIONS: tuple[tuple[str, str], ...] = (
    ("is_bot", "INTEGER NOT NULL DEFAULT 0"),
    ("is_premium", "INTEGER"),
    ("added_to_attachment_menu", "INTEGER"),
    ("raw_json", "TEXT NOT NULL DEFAULT '{}'"),
)


class Database:
    """Bitta jarayon uchun aiosqlite ulanishi.

    aiosqlite standart `sqlite3` ni alohida threadda chaqiradi, shuning uchun
    so'rovlar aiogram event loopini bloklamaydi. SQLite bitta yozuvchini
    qo'llaydi: botning bitta nusxasi shu faylga yozishi kerak.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self._connection: aiosqlite.Connection | None = None

    @property
    def connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            raise RuntimeError("Baza ulanmagan. Avval connect() ni chaqiring.")
        return self._connection

    async def connect(self) -> None:
        if self._connection is not None:
            return

        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = await aiosqlite.connect(self.path)
        connection.row_factory = aiosqlite.Row
        await connection.execute("PRAGMA journal_mode=WAL;")
        await connection.execute("PRAGMA foreign_keys=ON;")
        await connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        await _ensure_user_columns(connection)
        await connection.commit()
        self._connection = connection

    async def close(self) -> None:
        if self._connection is None:
            return
        await self._connection.close()
        self._connection = None


async def _ensure_user_columns(connection: aiosqlite.Connection) -> None:
    cursor = await connection.execute("PRAGMA table_info(users)")
    rows = await cursor.fetchall()
    existing = {row["name"] for row in rows}
    for name, definition in _USER_COLUMN_ADDITIONS:
        if name not in existing:
            await connection.execute(f"ALTER TABLE users ADD COLUMN {name} {definition}")
