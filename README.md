# safe-bot

Telegram bot. Telegram Business ulanishidagi chatlarni kuzatadi. APK yoki xavfli havola kelsa, xabarni o‘chiradi va bot orqali egasiga qaysi chat yuborganini yozadi. `/start` da salomlashadi va foydalanuvchini SQLite bazasiga yozadi.

## Talablar

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## Ishga tushirish

```bash
uv sync
cp .env.example .env
```

`.env` ichidagi `BOT_TOKEN` ni BotFather bergan token bilan almashtiring.

Botni Telegram Business sozlamasida ulang va unga chatlardagi xabarlarni o‘chirish ruxsatini bering. Xavfli domen va fayl xeshlarini `blocklists/local.txt` ga yozing. `VIRUSTOTAL_API_KEY` bo‘lsa, qoidalardan o‘tgan havola va ilova fayl VirusTotal da ham tekshiriladi. Kalit bo‘lmasa, ilova fayllari (apk, exe va shunga o‘xshash) baribir o‘chiriladi.

Ogohlantirish mijoz chatiga emas, bot bilan egasi o‘rtasidagi chatga ketadi. Unda chat nomi, chat ID, yuboruvchi, fayl yoki domen va qisqa sabab bor. To‘liq havola yozilmaydi.

```bash
uv run safe-bot
```

## Docker

`.env` faylida `BOT_TOKEN` bo‘lishi kerak.

```bash
docker compose up -d --build
docker compose logs -f bot
```

Baza Docker volume ichida saqlanadi. To‘xtatish: `docker compose down`.

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
- `src/safe_bot/safety/` — qoidalar, blok-ro‘yxat va VirusTotal
- `blocklists/local.txt` — qo‘lda to‘ldiriladigan domen va SHA-256 ro‘yxati

`aiosqlite` standart kutubxona `sqlite3` ni alohida threadda ishlatadi. Shuning uchun so‘rovlar aiogram event loopini to‘xtatmaydi.
