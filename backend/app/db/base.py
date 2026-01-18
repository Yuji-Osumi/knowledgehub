import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ==================================================
# Base
# ==================================================
class Base(DeclarativeBase):
    """すべての ORM モデルの基底クラス"""

    def __repr__(self) -> str:
        cols = ", ".join(f"{k}={v}" for k, v in self.__dict__.items() if not k.startswith("_"))
        return f"<{self.__class__.__name__}({cols})>"


# ==================================================
# ID / 公開ID
# ==================================================
class IdMixin:
    """内部ID（全エンティティ共通）"""

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )


class PublicIdMixin:
    """外部公開ID（主要エンティティ用）"""

    public_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )


# ==================================================
# 有効フラグ（論理削除）
# ==================================================
class ValidityMixin:
    """論理削除・有効フラグ"""

    is_valid: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )


# ==================================================
# 作成・更新ユーザー
# ==================================================
class AuditUserMixin:
    """
    作成者・更新者
    """

    created_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    updated_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )


# ==================================================
# 作成・更新日時
# ==================================================
class TimestampMixin:
    """作成日時・更新日時"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
