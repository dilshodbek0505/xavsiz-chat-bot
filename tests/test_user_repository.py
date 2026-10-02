from safe_bot.db.repositories.users import UserRepository
from safe_bot.domain.users import TelegramProfile


async def test_upsert_creates_user(users: UserRepository) -> None:
    profile = TelegramProfile(
        id=42,
        is_bot=False,
        first_name="Ali",
        last_name="Valiyev",
        username="ali",
        language_code="uz",
        is_premium=True,
        added_to_attachment_menu=False,
        raw={"id": 42, "first_name": "Ali", "can_join_groups": False},
    )

    saved = await users.upsert(profile)

    assert saved.id == 42
    assert saved.is_bot is False
    assert saved.first_name == "Ali"
    assert saved.last_name == "Valiyev"
    assert saved.username == "ali"
    assert saved.language_code == "uz"
    assert saved.is_premium is True
    assert saved.added_to_attachment_menu is False
    assert saved.raw["can_join_groups"] is False
    assert saved.created_at
    assert saved.updated_at == saved.created_at


async def test_upsert_updates_profile_and_keeps_created_at(users: UserRepository) -> None:
    await users.upsert(TelegramProfile(id=7, first_name="Ali", username="old"))
    created = await users.get(7)
    assert created is not None

    updated = await users.upsert(
        TelegramProfile(
            id=7,
            first_name="Vali",
            username="new",
            language_code="ru",
            is_premium=True,
            added_to_attachment_menu=True,
            raw={"id": 7, "supports_inline_queries": True},
        )
    )

    assert updated.id == 7
    assert updated.first_name == "Vali"
    assert updated.username == "new"
    assert updated.language_code == "ru"
    assert updated.is_premium is True
    assert updated.added_to_attachment_menu is True
    assert updated.raw["supports_inline_queries"] is True
    assert updated.created_at == created.created_at
    assert await users.get(7) == updated


async def test_get_returns_none_for_unknown_user(users: UserRepository) -> None:
    assert await users.get(999) is None
