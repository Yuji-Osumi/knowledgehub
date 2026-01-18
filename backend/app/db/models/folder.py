from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditUserMixin, Base, IdMixin, PublicIdMixin, TimestampMixin, ValidityMixin


class Folder(Base, IdMixin, PublicIdMixin, ValidityMixin, AuditUserMixin, TimestampMixin):
    """フォルダテーブル"""

    __tablename__ = "folders"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("folders.id"),
        nullable=True,
    )
