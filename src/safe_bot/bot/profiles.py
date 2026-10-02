from aiogram.types import User

from safe_bot.domain.users import TelegramProfile


def profile_from_user(user: User) -> TelegramProfile:
    """Telegram `User` dagi barcha maydonlarni profilga ko'chiradi.

    Alohida ustunlar qidirish uchun. `raw` esa modeldagi qolgan maydonlarni ham
    saqlaydi, shu jumladan faqat botda keladigan bayroqlarni.
    """
    raw = user.model_dump(mode="json")
    return TelegramProfile(
        id=user.id,
        is_bot=user.is_bot,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        language_code=user.language_code,
        is_premium=user.is_premium,
        added_to_attachment_menu=user.added_to_attachment_menu,
        raw=raw,
    )
