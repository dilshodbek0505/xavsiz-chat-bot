from collections.abc import AsyncGenerator
from typing import Any

from aiogram.client.session.base import BaseSession
from aiogram.methods import DeleteBusinessMessages, GetBusinessConnection, SendMessage
from aiogram.methods.base import TelegramMethod, TelegramType
from aiogram.types import BusinessConnection, Update
from pydantic import SecretStr

from safe_bot.bot.factory import create_bot, create_dispatcher
from safe_bot.config import Settings
from safe_bot.db.repositories.business_connections import BusinessConnectionRepository
from safe_bot.db.repositories.users import UserRepository
from safe_bot.safety.blocklist import Blocklist
from safe_bot.safety.gate import SafetyGate


class RecordingSession(BaseSession):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[str] = []
        self.messages: list[tuple[int | str, str]] = []
        self.deleted: list[list[int]] = []

    async def close(self) -> None:
        return None

    async def make_request(
        self,
        bot: Any,
        method: TelegramMethod[TelegramType],
        timeout: int | None = None,
    ) -> TelegramType:
        self.calls.append(type(method).__name__)
        if isinstance(method, SendMessage):
            self.messages.append((method.chat_id, method.text or ""))
        if isinstance(method, DeleteBusinessMessages):
            self.deleted.append(list(method.message_ids))
        if isinstance(method, GetBusinessConnection):
            return BusinessConnection.model_validate(
                _connection(can_delete_all_messages=True)
            )  # type: ignore[return-value]
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


def _connection(*, can_delete_all_messages: bool, is_enabled: bool = True) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": "conn-1",
        "user": {"id": 15, "is_bot": False, "first_name": "Dilshod"},
        "user_chat_id": 15,
        "date": 1_710_000_000,
        "is_enabled": is_enabled,
    }
    if can_delete_all_messages:
        payload["rights"] = {"can_delete_all_messages": True}
    return payload


def _business_message(**message: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "message_id": 10,
        "date": 1_710_000_000,
        "business_connection_id": "conn-1",
        "chat": {
            "id": 99,
            "type": "private",
            "first_name": "Ali",
            "last_name": "Valiyev",
            "username": "ali",
        },
        "from": {
            "id": 99,
            "is_bot": False,
            "first_name": "Ali",
            "last_name": "Valiyev",
            "username": "ali",
        },
    }
    payload.update(message)
    return payload


async def _feed(
    users: UserRepository,
    connections: BusinessConnectionRepository,
    safety: SafetyGate,
    *updates: dict[str, object],
) -> RecordingSession:
    settings = Settings(bot_token=SecretStr("123456:test"), _env_file=None)
    bot = create_bot(settings)
    session = RecordingSession()
    bot.session = session
    dispatcher = create_dispatcher(users, connections, safety)
    for index, body in enumerate(updates, start=1):
        update = Update.model_validate({"update_id": index, **body}, context={"bot": bot})
        await dispatcher.feed_update(bot, update)
    await bot.session.close()
    return session


async def test_business_dangerous_link_is_deleted_and_owner_is_warned(
    users: UserRepository,
    connections: BusinessConnectionRepository,
) -> None:
    session = await _feed(
        users,
        connections,
        SafetyGate(Blocklist.parse("phishing.test")),
        {"business_connection": _connection(can_delete_all_messages=True)},
        {"business_message": _business_message(text="https://phishing.test/login")},
    )

    assert session.deleted == [[10]]
    assert len(session.messages) == 1
    chat_id, text = session.messages[0]
    assert chat_id == 15
    assert "o'chirildi" in text
    assert "Ali Valiyev (@ali)" in text
    assert "Chat ID: 99" in text
    assert "phishing.test" in text
    assert "http" not in text


async def test_business_apk_is_deleted_and_reported(
    users: UserRepository,
    connections: BusinessConnectionRepository,
) -> None:
    session = await _feed(
        users,
        connections,
        SafetyGate(Blocklist.parse("")),
        {"business_connection": _connection(can_delete_all_messages=True)},
        {
            "business_message": _business_message(
                document={
                    "file_id": "file",
                    "file_unique_id": "unique",
                    "file_name": "app.apk",
                    "mime_type": "application/vnd.android.package-archive",
                    "file_size": 128,
                }
            )
        },
    )

    assert session.deleted == [[10]]
    assert "app.apk" in session.messages[0][1]
    assert "Ali Valiyev (@ali)" in session.messages[0][1]


async def test_ordinary_business_message_is_left_alone(
    users: UserRepository,
    connections: BusinessConnectionRepository,
) -> None:
    session = await _feed(
        users,
        connections,
        SafetyGate(Blocklist.parse("")),
        {"business_connection": _connection(can_delete_all_messages=True)},
        {"business_message": _business_message(text="https://example.com/news")},
    )

    assert session.deleted == []
    assert session.messages == []


async def test_missing_delete_right_still_warns_the_owner(
    users: UserRepository,
    connections: BusinessConnectionRepository,
) -> None:
    session = await _feed(
        users,
        connections,
        SafetyGate(Blocklist.parse("phishing.test")),
        {"business_connection": _connection(can_delete_all_messages=False)},
        {"business_message": _business_message(text="https://phishing.test/login")},
    )

    assert session.deleted == []
    assert "O'chirib bo'lmadi" in session.messages[0][1]


async def test_unknown_connection_is_loaded_from_telegram(
    users: UserRepository,
    connections: BusinessConnectionRepository,
) -> None:
    session = await _feed(
        users,
        connections,
        SafetyGate(Blocklist.parse("phishing.test")),
        {"business_message": _business_message(text="https://phishing.test/login")},
    )

    assert "GetBusinessConnection" in session.calls
    assert session.deleted == [[10]]
    saved = await connections.get("conn-1")
    assert saved is not None
    assert saved.user_chat_id == 15
    assert saved.can_delete_all_messages is True


async def test_direct_private_message_is_not_inspected(
    users: UserRepository,
    connections: BusinessConnectionRepository,
) -> None:
    session = await _feed(
        users,
        connections,
        SafetyGate(Blocklist.parse("phishing.test")),
        {
            "message": {
                "message_id": 10,
                "date": 1_710_000_000,
                "chat": {"id": 15, "type": "private", "first_name": "Dilshod"},
                "from": {"id": 15, "is_bot": False, "first_name": "Dilshod"},
                "text": "https://phishing.test/login",
            }
        },
    )

    assert session.calls == []
