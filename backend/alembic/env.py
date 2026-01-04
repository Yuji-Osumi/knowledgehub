from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.db.base import Base
from app.db import models

# Alembic の設定オブジェクト
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# alembic.ini に記載されたログ設定を適用
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --autogenerate オプション時に比較対象とするメタデータを指定
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    オフラインモードでのマイグレーション実行
    DB への直接接続なしで SQL スクリプトのみを出力するモードです。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    オンラインモードでのマイグレーション実行
    実際にデータベースに接続してマイグレーションを適用するモードです。
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
