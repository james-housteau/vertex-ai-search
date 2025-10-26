"""Configuration for demo website."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    api_url: str = "https://search-api-546806894637.us-central1.run.app"
    host: str = "0.0.0.0"
    port: int = 8080

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
