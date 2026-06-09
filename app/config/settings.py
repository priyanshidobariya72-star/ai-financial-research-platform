from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOTENV_PATH = PROJECT_ROOT / ".env"

if DOTENV_PATH.exists():
    load_dotenv(DOTENV_PATH)


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # API Configuration
    api_title: str = "AI Financial Research Platform API"
    api_version: str = "0.1.0"
    debug: bool = False

    # Database Configuration
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/ai_financial_research_platform"
    database_echo: bool = False

    # Server Configuration
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # Feature Flags
    enable_docs: bool = True
    enable_redoc: bool = True

    class Config:
        env_file = str(DOTENV_PATH)
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
