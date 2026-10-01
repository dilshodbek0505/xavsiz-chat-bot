import logging

from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)


async def on_error(event: ErrorEvent) -> None:
    logger.error("Yangilanishni qayta ishlashda xato", exc_info=event.exception)
