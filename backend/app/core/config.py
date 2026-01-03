import os

from functools import lru_cache
from typing import List, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.logging import LogLevel


class AppSettings(BaseSettings):
    """全環境共通の基本設定"""

    # --- Environment ---
    app_env: Literal["local", "dev", "prod"] = "local"
    debug: bool = False
    log_level: LogLevel = "DEBUG"

    # --- Application ---
    app_name: str = "KnowledgeHub API"
    api_prefix: str = "/api"
    app_version: str = "0.1.0"

    # --- CORS ---
    cors_allow_origins: List[str] = []

    # --- Database ---
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


class LocalSettings(AppSettings):
    debug: bool = True
    log_level: LogLevel = "DEBUG"
    cors_allow_origins: List[str] = ["http://localhost:3000"]


class DevSettings(AppSettings):
    debug: bool = False
    log_level: LogLevel = "INFO"
    cors_allow_origins: List[str] = ["https://dev.example.com"]


class ProdSettings(AppSettings):
    debug: bool = False
    log_level: LogLevel = "INFO"
    cors_allow_origins: List[str] = ["https://example.com"]


@lru_cache
def get_settings() -> AppSettings:
    """環境変数 ENV に応じた Settings を返す"""

    env = os.getenv("APP_ENV", "local")

    if env == "prod":
        return ProdSettings()
    if env == "dev":
        return DevSettings()
    return LocalSettings()


settings = get_settings()
