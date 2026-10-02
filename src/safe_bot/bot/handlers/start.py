from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from safe_bot.bot.profiles import profile_from_user
from safe_bot.db.repositories.users import UserRepository
from safe_bot.services.greeting import build_greeting
from safe_bot.services.start import register_and_greet


async def on_start(message: Message, users: UserRepository) -> None:
    sender = message.from_user
    if sender is None:
        await message.answer(build_greeting(None))
        return

    text = await register_and_greet(users, profile_from_user(sender))
    await message.answer(text)


def build_start_router() -> Router:
    router = Router(name="start")
    router.message.register(on_start, CommandStart())
    return router
