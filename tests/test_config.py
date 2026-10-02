from pathlib import Path

import pytest
from pydantic import ValidationError

from safe_bot.config import Settings


def test_settings_require_bot_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BOT_TOKEN", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_read_token_and_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "123456:test-token")
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("BLOCKLIST_PATH", raising=False)
    monkeypatch.setenv("VIRUSTOTAL_API_KEY", "  ")

    settings = Settings(_env_file=None)

    assert settings.bot_token.get_secret_value() == "123456:test-token"
    assert settings.database_path == Path("data/bot.db")
    assert settings.log_level == "INFO"
    assert settings.blocklist_path == Path("blocklists/local.txt")
    assert settings.virustotal_api_key is None
