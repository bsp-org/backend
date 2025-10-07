"""Application configuration management."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")

    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="bible", alias="POSTGRES_DB")
    postgres_user: str = Field(default="bible_user", alias="POSTGRES_USER")
    postgres_password: str = Field(default="pleasechangeme", alias="POSTGRES_PASSWORD")

    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    # CORS configuration
    cors_origins: str | list[str] = Field(
        default=["*"],
        alias="CORS_ORIGINS",
        description="Allowed CORS origins (comma-separated in .env)",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse comma-separated CORS origins string into a list."""
        print(f"raw origins: {v}")
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
