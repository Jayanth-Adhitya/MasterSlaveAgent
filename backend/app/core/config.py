from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/agent_db"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # Gemini API
    google_api_key: str = ""

    # App
    app_name: str = "Agent Prototype"
    debug: bool = True

    model_config = SettingsConfigDict(
        # Try multiple .env locations for different environments
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    # Clear cache if in Docker (to re-read environment variables)
    if os.environ.get("DATABASE_URL"):
        get_settings.cache_clear()
    return Settings()
