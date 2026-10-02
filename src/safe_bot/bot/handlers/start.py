from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from safe_bot.bot.profiles import profile_from_user
from safe_bot.db.repositories.users import UserRepository
from safe_bot.services.greeting import build_greeting
from safe_bot.services.start import register_and_greet

BUSINESS_SETTINGS_URL = "tg://settings/business"

_STEPS = (
    "Chatlaringizni kuzatish uchun tugmani bosing. Sozlama ochilganda:\n"
    "1. Shu botni tanlang.\n"
    "2. Barcha shaxsiy chatlarni ulang.\n"
    "3. Xabarlarni o'chirish ruxsatini yoqing.\n\n"
    "Tugma ruxsatni o'zi bermaydi. BotFather da Business Mode yoqilgan bo'lishi kerak."
)


def build_start_text(first_name: str | None) -> str:
    return f"{build_greeting(first_name)}\n\n{_STEPS}"


def business_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Business sozlamasini ochish",
                    url=BUSINESS_SETTINGS_URL,
                )
            ]
        ]
    )


async def on_start(message: Message, users: UserRepository) -> None:
    sender = message.from_user
    if sender is None:
        text = build_start_text(None)
    else:
        await register_and_greet(users, profile_from_user(sender))
        text = build_start_text(sender.first_name)
    await message.answer(text, reply_markup=business_settings_keyboard())


def build_start_router() -> Router:
    router = Router(name="start")
    router.message.register(on_start, CommandStart())
    return router
