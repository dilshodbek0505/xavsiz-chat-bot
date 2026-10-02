from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from safe_bot.bot.handlers.errors import on_error
from safe_bot.bot.handlers.safety import build_safety_router
from safe_bot.bot.handlers.start import build_start_router
from safe_bot.bot.middlewares.database import ContextMiddleware
from safe_bot.config import Settings
from safe_bot.db.repositories.business_connections import BusinessConnectionRepository
from safe_bot.db.repositories.users import UserRepository
from safe_bot.safety.blocklist import Blocklist
from safe_bot.safety.gate import SafetyGate


def create_bot(settings: Settings) -> Bot:
    return Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(),
    )


def create_dispatcher(
    users: UserRepository,
    connections: BusinessConnectionRepository,
    safety: SafetyGate | None = None,
) -> Dispatcher:
    if safety is None:
        safety = SafetyGate(Blocklist.parse(""))
    dispatcher = Dispatcher()
    dispatcher.update.middleware(ContextMiddleware(users, safety, connections))
    dispatcher.include_router(build_safety_router())
    dispatcher.include_router(build_start_router())
    dispatcher.errors.register(on_error)
    return dispatcher
