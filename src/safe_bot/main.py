import asyncio
import logging

from safe_bot.bot.factory import create_bot, create_dispatcher
from safe_bot.config import Settings
from safe_bot.db.database import Database
from safe_bot.db.repositories.business_connections import BusinessConnectionRepository
from safe_bot.db.repositories.users import UserRepository
from safe_bot.logging_config import setup_logging
from safe_bot.safety.blocklist import Blocklist
from safe_bot.safety.external import VirusTotalChecker
from safe_bot.safety.gate import SafetyGate

logger = logging.getLogger(__name__)


async def run(settings: Settings | None = None) -> None:
    settings = settings or Settings()
    setup_logging(settings.log_level)

    database = Database(settings.database_path)
    await database.connect()
    users = UserRepository(database)
    connections = BusinessConnectionRepository(database)
    blocklist = Blocklist.load(settings.blocklist_path)
    external = None
    if settings.virustotal_api_key is not None:
        external = VirusTotalChecker(settings.virustotal_api_key.get_secret_value())
    safety = SafetyGate(blocklist, external)
    logger.info(
        "Blok-ro'yxat: %s domen, %s xesh. VirusTotal: %s",
        len(blocklist.domains),
        len(blocklist.sha256),
        "yoqilgan" if external is not None else "o'chiq",
    )
    bot = create_bot(settings)
    dispatcher = create_dispatcher(users, connections, safety)

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
