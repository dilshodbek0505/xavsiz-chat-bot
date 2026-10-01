from pathlib import Path

from pydantic import SecretStr
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
