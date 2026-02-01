import os
from functools import lru_cache
from typing import List, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """全環境共通の基本設定"""

    # --- Environment ---
    app_env: Literal["local", "dev", "prod"] = "local"
    debug: bool = False
    log_level: str = "DEBUG"

    # --- Application ---
    app_name: str = "KnowledgeHub API"
    api_prefix: str = "/api"
    app_version: str = "0.1.0"

    # --- CORS ---
    cors_allow_origins: List[str] = []

    # --- Database ---
    DATABASE_URL: str = ""

    # --- Session Management ---
    SESSION_TIMEOUT_HOURS: int = 24
    SECURE_COOKIE: bool = False  # Cookie の Secure フラグ（本番環境では True）

    # --- Redis ---
    REDIS_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding="utf-8",
    )


class LocalSettings(AppSettings):
    debug: bool = True
    log_level: str = "DEBUG"
    cors_allow_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    SECURE_COOKIE: bool = False


class DevSettings(AppSettings):
    debug: bool = False
    log_level: str = "INFO"
    cors_allow_origins: List[str] = ["https://dev.example.com"]
    SECURE_COOKIE: bool = True


class ProdSettings(AppSettings):
    debug: bool = False
    log_level: str = "INFO"
    cors_allow_origins: List[str] = ["https://example.com"]
    SECURE_COOKIE: bool = True


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
