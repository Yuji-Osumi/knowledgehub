import logging

from typing import Literal

# レベルをリテラルで定義
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def setup_logging(log_level: LogLevel = "INFO") -> None:
    """
    アプリケーション全体の logging 設定
    """
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )

    # 特定のライブラリ（UvicornやSQLAlchemy等）のログレベルを個別に調整
    loggers = ["uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"]
    for logger_name in loggers:
        logging.getLogger(logger_name).setLevel(log_level)

    logger = logging.getLogger("app")
    logger.info(f"Logging initialized with level: {log_level}")
