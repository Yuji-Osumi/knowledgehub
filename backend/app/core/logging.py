import logging.config
from typing import Literal

from app.core.config import settings

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | None


def setup_logging(log_level: LogLevel = None) -> None:
    """
    アプリケーション全体のロギング設定を dictConfig で一括定義する。
    RichHandler を使用し、Uvicorn のログも統合する。
    """
    if log_level is None:
        log_level = "DEBUG" if settings.debug else "INFO"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,  # 既存のロガー（uvicorn等）を無効化せず共存させる
        "formatters": {
            "simple": {
                "format": "%(message)s",  # RichHandlerが時刻やレベルを装飾するためメッセージのみ
                "datefmt": "[%X]",
            },
        },
        "handlers": {
            "rich": {
                "class": "rich.logging.RichHandler",
                "level": log_level,
                "formatter": "simple",
                "rich_tracebacks": True,  # スタックトレースをリッチに表示
                # "tracebacks_show_locals": True,  # 変数の中身を表示
                # "markup": True,
            },
        },
        "loggers": {
            "app": {
                "handlers": ["rich"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["rich"],
                "level": log_level,
                "propagate": False,  # Rootへ流して二重出力されるのを防ぐ
            },
            "uvicorn.access": {
                "handlers": ["rich"],
                "level": "INFO",  # アクセスログは常にINFO程度で出す
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["rich"],
                "level": "WARNING",  # SQL実行ログがうるさい場合はWARNINGに
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["rich"],
            "level": log_level,
        },
    }

    logging.config.dictConfig(logging_config)

    logger = logging.getLogger("app")
    logger.info(
        f"Logging initialized with level: [bold blue]{log_level}[/bold blue]",
        extra={"markup": True},
    )
