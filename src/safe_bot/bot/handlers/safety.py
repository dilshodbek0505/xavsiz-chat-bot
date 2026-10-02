import hashlib
import logging
from io import BytesIO

from aiogram import Bot, Router
from aiogram.enums import MessageEntityType
from aiogram.exceptions import TelegramAPIError
from aiogram.methods import DeleteBusinessMessages, GetBusinessConnection
from aiogram.types import BusinessConnection, Message

from safe_bot.bot.business import alert_source_from_message, deletion_rights
from safe_bot.db.repositories.business_connections import BusinessConnectionRepository
from safe_bot.domain.business import BusinessLink
from safe_bot.safety.alert import build_business_alert, hosts_from_urls
from safe_bot.safety.gate import HashError, SafetyGate
from safe_bot.safety.models import Submission
from safe_bot.safety.urls import extract_urls

logger = logging.getLogger(__name__)

# Oddiy bot API 20 MB dan katta faylni yuklab olmaydi.
MAX_DOWNLOAD_BYTES = 20 * 1024 * 1024


async def on_business_connection(
    connection: BusinessConnection,
    connections: BusinessConnectionRepository,
) -> None:
    await _save_connection(connections, connection)
    logger.info(
        "Business ulanish yangilandi id=%s enabled=%s",
        connection.id,
        connection.is_enabled,
    )


async def on_business_message(
    message: Message,
    safety: SafetyGate,
    bot: Bot,
    connections: BusinessConnectionRepository,
) -> None:
    connection_id = message.business_connection_id
    if not connection_id:
        return
    urls = message_urls(message)
    document = message.document
    if document is None and not urls:
        return

    link = await _resolve_link(bot, connections, connection_id)
    if link is None:
        logger.info("Business ulanish yo'q yoki o'chiq: %s", connection_id)
        return

    submission = Submission(
        urls=urls,
        file_name=document.file_name if document else None,
        mime_type=document.mime_type if document else None,
    )

    async def file_hash() -> str | None:
        if document is None:
            return None
        if document.file_size is not None and document.file_size > MAX_DOWNLOAD_BYTES:
            raise HashError("file_too_large")
        buffer = BytesIO()
        try:
            await bot.download(document, destination=buffer)
        except TelegramAPIError:
            logger.exception("Fayl yuklab olinmadi")
            return None
        return hashlib.sha256(buffer.getvalue()).hexdigest()

    decision = await safety.evaluate(
        submission,
        file_hash=file_hash if document is not None else None,
    )
    if not decision.delete:
        return

    deleted = False
    if link.can_delete_all_messages:
        try:
            await bot(
                DeleteBusinessMessages(
                    business_connection_id=connection_id,
                    message_ids=[message.message_id],
                )
            )
            deleted = True
        except TelegramAPIError:
            logger.exception("Business xabar o'chirilmadi")

    source = alert_source_from_message(
        message.chat,
        message.from_user,
        document.file_name if document else None,
        hosts_from_urls(urls),
    )
    logger.info(
        "Business ogohlantirish chat=%s deleted=%s reasons=%s",
        source.chat_id,
        deleted,
        [reason.code for reason in decision.reasons],
    )
    try:
        await bot.send_message(
            link.user_chat_id,
            build_business_alert(source, decision, deleted=deleted),
        )
    except TelegramAPIError:
        logger.exception("Ogohlantirish yuborilmadi")


def build_safety_router() -> Router:
    router = Router(name="safety")
    router.business_connection.register(on_business_connection)
    router.business_message.register(on_business_message)
    return router


def message_urls(message: Message) -> tuple[str, ...]:
    found = _urls_from_part(message.text, message.entities)
    found.extend(_urls_from_part(message.caption, message.caption_entities))
    unique: list[str] = []
    seen: set[str] = set()
    for url in found:
        if url in seen:
            continue
        seen.add(url)
        unique.append(url)
    return tuple(unique)


def _urls_from_part(text: str | None, entities: object) -> list[str]:
    if not text:
        return []
    found: list[str] = []
    for entity in entities or ():
        if entity.type == MessageEntityType.URL:
            found.append(entity.extract_from(text))
        elif entity.type == MessageEntityType.TEXT_LINK and entity.url:
            found.append(entity.url)
    found.extend(extract_urls(text))
    return found


async def _resolve_link(
    bot: Bot,
    connections: BusinessConnectionRepository,
    connection_id: str,
) -> BusinessLink | None:
    stored = await connections.get(connection_id)
    if stored is not None:
        return stored if stored.is_enabled else None
    try:
        remote = await bot(GetBusinessConnection(business_connection_id=connection_id))
    except TelegramAPIError:
        logger.exception("Business ulanish olinmadi")
        return None
    if not isinstance(remote, BusinessConnection):
        logger.error("Business ulanish javobi kutilmagan turda")
        return None
    saved = await _save_connection(connections, remote)
    return saved if saved.is_enabled else None


async def _save_connection(
    connections: BusinessConnectionRepository,
    connection: BusinessConnection,
) -> BusinessLink:
    can_delete_all, can_delete_sent = deletion_rights(connection)
    return await connections.upsert(
        connection_id=connection.id,
        user_id=connection.user.id,
        user_chat_id=connection.user_chat_id,
        is_enabled=connection.is_enabled,
        can_delete_all_messages=can_delete_all,
        can_delete_sent_messages=can_delete_sent,
    )
