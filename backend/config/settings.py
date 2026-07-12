from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    database_url: str = Field(default="sqlite:///./backend/database/app.db", alias="DATABASE_URL")
    upload_dir: Path = Field(default=Path("backend/uploads"), alias="UPLOAD_DIR")
    log_dir: Path = Field(default=Path("backend/logs"), alias="LOG_DIR")
    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(default=None, alias="TELEGRAM_CHAT_ID")
    emergency_threshold: float = Field(default=0.8, alias="EMERGENCY_THRESHOLD")
    whisper_model_name: str = Field(default="base", alias="WHISPER_MODEL_NAME")
    whisper_language: str | None = Field(default=None, alias="WHISPER_LANGUAGE")
    whisper_device: str = Field(default="cpu", alias="WHISPER_DEVICE")
    bert_model_name: str = Field(default="bert-base-uncased", alias="BERT_MODEL_NAME")
    bert_device: str = Field(default="cpu", alias="BERT_DEVICE")
    bert_emergency_labels: str = Field(
        default="Emergency,EMERGENCY,LABEL_1",
        alias="BERT_EMERGENCY_LABELS",
    )
    bert_normal_labels: str = Field(
        default="Normal,NORMAL,LABEL_0",
        alias="BERT_NORMAL_LABELS",
    )
    challenge_ttl_seconds: int = Field(default=120, alias="CHALLENGE_TTL_SECONDS")
    auth_token_secret: str = Field(default="change-this-auth-token-secret", alias="AUTH_TOKEN_SECRET")
    auth_token_ttl_seconds: int = Field(default=600, alias="AUTH_TOKEN_TTL_SECONDS")
    server_schnorr_secret_key: int = Field(default=7, alias="SERVER_SCHNORR_SECRET_KEY")

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_flag(cls, value):
        """Accept common environment names accidentally supplied as DEBUG."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod"}:
                return False
            if normalized in {"development", "dev", "debug"}:
                return True
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
