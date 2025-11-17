from pydantic_settings import BaseSettings
from functools import lru_cache


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

    class Config:
        env_file = "../.env"  # Look for .env in parent directory (project root)
        extra = "ignore"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
