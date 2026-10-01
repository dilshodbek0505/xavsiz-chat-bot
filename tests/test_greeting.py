from safe_bot.services.greeting import build_greeting


def test_greeting_includes_first_name() -> None:
    assert build_greeting("Ahror") == "Salom, Ahror!"


def test_greeting_without_name_stays_plain() -> None:
    assert build_greeting(None) == "Salom!"
    assert build_greeting("   ") == "Salom!"
