from pathlib import Path

import aiosqlite

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


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
        await connection.commit()
        self._connection = connection

    async def close(self) -> None:
        if self._connection is None:
            return
        await self._connection.close()
        self._connection = None
