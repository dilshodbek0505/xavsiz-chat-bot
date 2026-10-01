from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TelegramProfile:
    """Telegramdan kelgan foydalanuvchi profili. Bazaga bog'liq emas."""

    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None


@dataclass(frozen=True, slots=True)
class UserRecord:
    """Bazada saqlangan foydalanuvchi."""

    id: int
    first_name: str
    last_name: str | None
    username: str | None
    language_code: str | None
    created_at: str
    updated_at: str
