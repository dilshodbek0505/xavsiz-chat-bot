from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from safe_bot.db.repositories.users import UserRepository


class UserRepositoryMiddleware(BaseMiddleware):
    """Har bir yangilanishga foydalanuvchilar repository sini uzatadi."""

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["users"] = self._users
        return await handler(event, data)
