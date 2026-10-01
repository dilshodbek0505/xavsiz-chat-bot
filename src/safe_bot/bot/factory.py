from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from safe_bot.bot.handlers.errors import on_error
from safe_bot.bot.handlers.start import router as start_router
from safe_bot.bot.middlewares.database import UserRepositoryMiddleware
from safe_bot.config import Settings
from safe_bot.db.repositories.users import UserRepository


def create_bot(settings: Settings) -> Bot:
    return Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(),
    )


def create_dispatcher(users: UserRepository) -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.update.middleware(UserRepositoryMiddleware(users))
    dispatcher.include_router(start_router)
    dispatcher.errors.register(on_error)
    return dispatcher
