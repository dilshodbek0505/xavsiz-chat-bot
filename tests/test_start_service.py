from safe_bot.db.repositories.users import UserRepository
from safe_bot.domain.users import TelegramProfile
from safe_bot.services.start import register_and_greet


async def test_register_and_greet_saves_user_and_returns_greeting(
    users: UserRepository,
) -> None:
    profile = TelegramProfile(id=15, first_name="Dilshod", username="dilshod")

    text = await register_and_greet(users, profile)

    assert text == "Salom, Dilshod!"
    saved = await users.get(15)
    assert saved is not None
    assert saved.username == "dilshod"
    assert saved.first_name == "Dilshod"
