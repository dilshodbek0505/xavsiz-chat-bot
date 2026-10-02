from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BusinessLink:
    """Telegram Business ulanishi. Ogohlantirish `user_chat_id` ga ketadi."""

    id: str
    user_id: int
    user_chat_id: int
    is_enabled: bool
    can_delete_all_messages: bool
    can_delete_sent_messages: bool
    updated_at: str
