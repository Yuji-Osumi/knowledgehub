from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# すべてのモデルが継承する Base
class Base(DeclarativeBase):
    # インスタンスの文字列表現を定義するメソッド。カラム名と値を表示
    def __repr__(self) -> str:
        cols = ", ".join(f"{k}={v}" for k, v in self.__dict__.items() if not k.startswith("_"))
        return f"<{self.__class__.__name__}({cols})>"


# 共通カラム Mixin
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
