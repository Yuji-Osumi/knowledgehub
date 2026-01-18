from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditUserMixin, Base, IdMixin, PublicIdMixin, TimestampMixin, ValidityMixin


class Tag(Base, IdMixin, PublicIdMixin, ValidityMixin, AuditUserMixin, TimestampMixin):
    """タグテーブル"""

    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_tags_user_id_name"),)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
