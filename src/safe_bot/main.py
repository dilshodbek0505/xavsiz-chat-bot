import asyncio
import logging

from safe_bot.bot.factory import create_bot, create_dispatcher
from safe_bot.config import Settings
from safe_bot.db.database import Database
from safe_bot.db.repositories.users import UserRepository
from safe_bot.logging_config import setup_logging

logger = logging.getLogger(__name__)


async def run(settings: Settings | None = None) -> None:
    settings = settings or Settings()
    setup_logging(settings.log_level)

    database = Database(settings.database_path)
    await database.connect()
    users = UserRepository(database)
    bot = create_bot(settings)
    dispatcher = create_dispatcher(users)

    logger.info("Bot polling boshlandi")
    try:
        await dispatcher.start_polling(
            bot,
            allowed_updates=dispatcher.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()
        await database.close()
        logger.info("Bot to'xtadi")


def main() -> None:
    asyncio.run(run())
