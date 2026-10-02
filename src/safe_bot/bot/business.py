from aiogram.types import BusinessConnection, Chat, User

from safe_bot.safety.alert import AlertSource


def deletion_rights(connection: BusinessConnection) -> tuple[bool, bool]:
    rights = connection.rights
    if rights is None:
        return False, False
    return bool(rights.can_delete_all_messages), bool(rights.can_delete_sent_messages)


def alert_source_from_message(message_chat: Chat, sender: User | None, file_name: str | None, hosts: tuple[str, ...]) -> AlertSource:
    return AlertSource(
        chat_id=message_chat.id,
        chat_name=_chat_name(message_chat),
        chat_username=message_chat.username,
        sender_name=_user_name(sender),
        sender_username=sender.username if sender else None,
        file_name=file_name,
        hosts=hosts,
    )


def _chat_name(chat: Chat) -> str:
    if chat.title:
        return chat.title
    return _join_name(chat.first_name, chat.last_name)


def _user_name(user: User | None) -> str:
    if user is None:
        return "noma'lum"
    return _join_name(user.first_name, user.last_name)


def _join_name(first: str | None, last: str | None) -> str:
    parts = [part.strip() for part in (first, last) if part and part.strip()]
    return " ".join(parts) if parts else "noma'lum"
