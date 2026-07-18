from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings validated via Pydantic v2."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General System configurations
    ENV: Literal["development", "production", "testing"] = "development"
    PROJECT_NAME: str = "KPIs-Servicios"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Database configurations
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "kpis_servicios"
    POSTGRES_PORT: int = 5432

    # Redis Cache configurations
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Logging settings
    LOG_LEVEL: str = "INFO"

    # Allowed / Trusted hosts for security middleware
    ALLOWED_HOSTS: list[str] = ["*"]

    @property
    def database_url(self) -> str:
        """Construct synchronous SQLAlchemy database connection URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def database_async_url(self) -> str:
        """Construct asynchronous SQLAlchemy database connection URL."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


@lru_cache
def get_settings() -> Settings:
    """Load settings instance cached as a singleton."""
    return Settings()
