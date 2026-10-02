from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class TelegramProfile:
    """Telegramdan kelgan foydalanuvchi. `raw` — yuborilgan to'liq obyekt."""

    id: int
    first_name: str
    is_bot: bool = False
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool | None = None
    added_to_attachment_menu: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UserRecord:
    """Bazada saqlangan foydalanuvchi."""

    id: int
    first_name: str
    is_bot: bool
    last_name: str | None
    username: str | None
    language_code: str | None
    is_premium: bool | None
    added_to_attachment_menu: bool | None
    raw: dict[str, Any]
    created_at: str
    updated_at: str
