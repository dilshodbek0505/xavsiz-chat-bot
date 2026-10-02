from collections.abc import AsyncGenerator
from typing import Any

from aiogram.client.session.base import BaseSession
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramMethod, TelegramType
from aiogram.types import Update
from pydantic import SecretStr

from safe_bot.bot.factory import create_bot, create_dispatcher
from safe_bot.config import Settings
from safe_bot.db.repositories.business_connections import BusinessConnectionRepository
from safe_bot.db.repositories.users import UserRepository


class RecordingSession(BaseSession):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []
        self.markups: list[object] = []

    async def close(self) -> None:
        return None

    async def make_request(
        self,
        bot: Any,
        method: TelegramMethod[TelegramType],
        timeout: int | None = None,
    ) -> TelegramType:
        if isinstance(method, SendMessage):
            self.messages.append(method.text or "")
            self.markups.append(method.reply_markup)
        return True  # type: ignore[return-value]

    async def stream_content(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        timeout: int = 30,
        chunk_size: int = 65536,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes, None]:
        yield b""


async def test_start_command_greets_and_stores_user(
    users: UserRepository,
    connections: BusinessConnectionRepository,
) -> None:
    settings = Settings(bot_token=SecretStr("123456:test"), _env_file=None)
    bot = create_bot(settings)
    session = RecordingSession()
    bot.session = session
    dispatcher = create_dispatcher(users, connections)
    update = Update.model_validate(
        {
            "update_id": 1,
            "message": {
                "message_id": 10,
                "date": 1_710_000_000,
                "chat": {"id": 15, "type": "private"},
                "from": {
                    "id": 15,
                    "is_bot": False,
                    "first_name": "Dilshod",
                    "last_name": "Aka",
                    "username": "dilshod",
                    "language_code": "uz",
                    "is_premium": True,
                    "added_to_attachment_menu": True,
                },
                "text": "/start",
                "entities": [{"type": "bot_command", "offset": 0, "length": 6}],
            },
        },
        context={"bot": bot},
    )

    await dispatcher.feed_update(bot, update)

    assert len(session.messages) == 1
    assert session.messages[0].startswith("Salom, Dilshod!")
    assert "Shu botni tanlang" in session.messages[0]
    assert "Barcha shaxsiy chatlar" in session.messages[0]
    assert "o'chirish" in session.messages[0]
    assert "Business Mode" in session.messages[0]
    markup = session.markups[0]
    button = markup.inline_keyboard[0][0]
    assert button.text
    assert button.url == "tg://settings/business/bots"
    assert len(markup.inline_keyboard) == 1
    assert len(markup.inline_keyboard[0]) == 1
    saved = await users.get(15)
    assert saved is not None
    assert saved.is_bot is False
    assert saved.first_name == "Dilshod"
    assert saved.last_name == "Aka"
    assert saved.username == "dilshod"
    assert saved.language_code == "uz"
    assert saved.is_premium is True
    assert saved.added_to_attachment_menu is True
    assert saved.raw["id"] == 15
    assert saved.raw["is_premium"] is True
    await bot.session.close()
