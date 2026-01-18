from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditUserMixin, Base, IdMixin, PublicIdMixin, TimestampMixin, ValidityMixin


class User(Base, IdMixin, PublicIdMixin, ValidityMixin, AuditUserMixin, TimestampMixin):
    """ユーザーテーブル"""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
