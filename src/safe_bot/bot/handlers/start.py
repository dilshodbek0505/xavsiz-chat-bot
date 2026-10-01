from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from safe_bot.db.repositories.users import UserRepository
from safe_bot.domain.users import TelegramProfile
from safe_bot.services.greeting import build_greeting
from safe_bot.services.start import register_and_greet

router = Router(name="start")


@router.message(CommandStart())
async def on_start(message: Message, users: UserRepository) -> None:
    sender = message.from_user
    if sender is None:
        await message.answer(build_greeting(None))
        return

    text = await register_and_greet(
        users,
        TelegramProfile(
            id=sender.id,
            first_name=sender.first_name,
            last_name=sender.last_name,
            username=sender.username,
            language_code=sender.language_code,
        ),
    )
    await message.answer(text)
