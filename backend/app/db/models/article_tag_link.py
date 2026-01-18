from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditUserMixin, Base, IdMixin, TimestampMixin, ValidityMixin


class ArticleTagLink(Base, IdMixin, ValidityMixin, AuditUserMixin, TimestampMixin):
    """記事―タグ中間テーブル"""

    __tablename__ = "article_tag_links"
    __table_args__ = (
        UniqueConstraint("article_id", "tag_id", name="uq_article_tag_links_article_id_tag_id"),
    )

    article_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("articles.id"),
        nullable=False,
    )

    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tags.id"),
        nullable=False,
    )
