# safe-bot

Telegram bot. Hozircha foydalanuvchi `/start` bosganda salomlashadi va profilini SQLite bazasiga yozadi.

## Talablar

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## Ishga tushirish

```bash
uv sync
cp .env.example .env
```

`.env` ichidagi `BOT_TOKEN` ni BotFather bergan token bilan almashtiring.

```bash
uv run safe-bot
```

## Tekshirish

```bash
uv run pytest
```

## Tuzilma

- `src/safe_bot/main.py` — ilovani yig‘adi va pollingni ishga tushiradi
- `src/safe_bot/config.py` — sozlamalar (`.env`)
- `src/safe_bot/bot/` — aiogram: handler, middleware, dispatcher
- `src/safe_bot/services/` — bot javobi va foydalanuvchini saqlash
- `src/safe_bot/db/` — aiosqlite ulanishi va repository
- `src/safe_bot/domain/` — bazaga bog‘liq bo‘lmagan modellar

`aiosqlite` standart kutubxona `sqlite3` ni alohida threadda ishlatadi. Shuning uchun so‘rovlar aiogram event loopini to‘xtatmaydi.
