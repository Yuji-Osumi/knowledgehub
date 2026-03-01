from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==================================================
# リクエスト用Schema
# ==================================================
class ArticleCreate(BaseModel):
    """記事作成リクエスト"""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="記事タイトル",
    )

    content: str = Field(
        ...,
        min_length=1,
        description="記事本文",
    )

    folder_id: int | None = Field(
        default=None,
        description="フォルダID（内部ID）",
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, title):
        """titleが空白のみでないことを検証"""
        if not title.strip():
            raise ValueError("記事タイトルを入力してください")
        return title

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, content):
        """contentが空白のみでないことを検証"""
        if not content.strip():
            raise ValueError("記事本文を入力してください")
        return content


class ArticleUpdate(BaseModel):
    """記事更新リクエスト"""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="記事タイトル",
    )

    content: str = Field(
        ...,
        min_length=1,
        description="記事本文",
    )

    folder_id: int | None = Field(
        default=None,
        description="フォルダID（内部ID）",
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, title):
        """titleが空白のみでないことを検証"""
        if not title.strip():
            raise ValueError("記事タイトルは空白のみでは指定できません")
        return title

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, content):
        """contentが空白のみでないことを検証"""
        if not content.strip():
            raise ValueError("記事本文は空白のみでは指定できません")
        return content


# ==================================================
# レスポンス用Schema
# ==================================================
class ArticleDetailResponse(BaseModel):
    """記事レスポンス"""

    public_id: UUID = Field(description="外部公開ID（API/URL用）")
    title: str = Field(description="記事タイトル")
    content: str = Field(description="記事本文")
    folder_id: int | None = Field(description="フォルダID")
    created_at: datetime = Field(description="作成日時")
    updated_at: datetime = Field(description="更新日時")

    model_config = ConfigDict(from_attributes=True)


# ==================================================
# リスト用Schema（軽量版）
# ==================================================
class ArticleListItem(BaseModel):
    """記事一覧アイテム"""

    public_id: UUID = Field(description="外部公開ID（API/URL用）")
    title: str = Field(description="記事タイトル")
    created_at: datetime = Field(description="作成日時")
    updated_at: datetime = Field(description="更新日時")

    model_config = ConfigDict(from_attributes=True)
