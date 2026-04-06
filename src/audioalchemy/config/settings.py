"""Application settings loaded from environment variables and .env file.

Uses Pydantic v2 BaseSettings for strongly-typed, validated configuration.
All settings can be overridden via environment variables prefixed with
``AUDIOALCHEMY_``.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Top-level application configuration.

    Values are resolved in this priority order (highest first):
    1. Environment variables (``AUDIOALCHEMY_*``)
    2. ``.env`` file in the working directory
    3. Field defaults defined here
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AUDIOALCHEMY_",
        case_sensitive=False,
    )

    default_format: str = Field(
        default="mp3",
        description="Default output audio format (mp3, wav, flac, ogg, aac).",
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )


def get_settings() -> Settings:
    """Return a fully resolved Settings instance.

    Call this once at startup and pass the result where needed rather than
    constructing Settings repeatedly.
    """
    return Settings()
