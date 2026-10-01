from safe_bot.db.repositories.users import UserRepository
from safe_bot.domain.users import TelegramProfile
from safe_bot.services.greeting import build_greeting


async def register_and_greet(users: UserRepository, profile: TelegramProfile) -> str:
    """Foydalanuvchini saqlaydi va unga yuboriladigan salom matnini qaytaradi."""
    await users.upsert(profile)
    return build_greeting(profile.first_name)
