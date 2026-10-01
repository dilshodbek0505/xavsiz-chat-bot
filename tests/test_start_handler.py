from collections.abc import AsyncGenerator
from typing import Any

from aiogram.client.session.base import BaseSession
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramMethod, TelegramType
from aiogram.types import Update
from pydantic import SecretStr

from safe_bot.bot.factory import create_bot, create_dispatcher
from safe_bot.config import Settings
from safe_bot.db.repositories.users import UserRepository


class RecordingSession(BaseSession):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

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


async def test_start_command_greets_and_stores_user(users: UserRepository) -> None:
    settings = Settings(bot_token=SecretStr("123456:test"), _env_file=None)
    bot = create_bot(settings)
    session = RecordingSession()
    bot.session = session
    dispatcher = create_dispatcher(users)
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
                    "username": "dilshod",
                },
                "text": "/start",
                "entities": [{"type": "bot_command", "offset": 0, "length": 6}],
            },
        },
        context={"bot": bot},
    )

    await dispatcher.feed_update(bot, update)

    assert session.messages == ["Salom, Dilshod!"]
    saved = await users.get(15)
    assert saved is not None
    assert saved.first_name == "Dilshod"
    assert saved.username == "dilshod"
    await bot.session.close()
