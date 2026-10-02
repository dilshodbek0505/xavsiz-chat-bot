from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from safe_bot.db.repositories.business_connections import BusinessConnectionRepository
from safe_bot.db.repositories.users import UserRepository
from safe_bot.safety.gate import SafetyGate


class ContextMiddleware(BaseMiddleware):
    """Handlerlarga baza va tekshiruv xizmatini beradi."""

    def __init__(
        self,
        users: UserRepository,
        safety: SafetyGate,
        connections: BusinessConnectionRepository,
    ) -> None:
        self._users = users
        self._safety = safety
        self._connections = connections

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["users"] = self._users
        data["safety"] = self._safety
        data["connections"] = self._connections
        return await handler(event, data)
