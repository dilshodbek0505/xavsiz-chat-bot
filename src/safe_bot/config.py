from pathlib import Path

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Jarayon sozlamalari. Qiymatlar muhit o'zgaruvchilari yoki `.env` dan olinadi."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: SecretStr
    database_path: Path = Path("data/bot.db")
    log_level: str = "INFO"
    blocklist_path: Path = Path("blocklists/local.txt")
    virustotal_api_key: SecretStr | None = None

    @field_validator("virustotal_api_key", mode="before")
    @classmethod
    def empty_api_key_is_absent(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value
