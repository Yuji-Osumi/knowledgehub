from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditUserMixin, Base, IdMixin, PublicIdMixin, TimestampMixin, ValidityMixin


class Article(Base, IdMixin, PublicIdMixin, ValidityMixin, AuditUserMixin, TimestampMixin):
    """記事テーブル"""

    __tablename__ = "articles"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    folder_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("folders.id"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
