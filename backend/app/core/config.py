from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # General Settings
    ENV: Literal["development", "production", "testing"] = "development"
    PROJECT_NAME: str = "KPIs-Servicios"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Database Settings
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "kpis_servicios"
    POSTGRES_PORT: int = 5432

    # Redis Cache Settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    # Logging Settings
    LOG_LEVEL: str = "INFO"

    @property
    def database_url(self) -> str:
        """Construct SQLAlchemy synchronous database URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def database_async_url(self) -> str:
        """Construct SQLAlchemy asynchronous database URL."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
