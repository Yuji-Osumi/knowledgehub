"""
共通スキーマ定義
"""

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """エラー詳細"""

    code: str = Field(description="エラーコード")
    message: str = Field(description="エラーメッセージ")
    details: Any | None = Field(default=None, description="詳細情報（任意）")


class ErrorResponse(BaseModel):
    """エラーレスポンス"""

    error: ErrorDetail

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Article with public_id xxx not found",
                        "details": None,
                    }
                }
            ]
        }
    }


class ValidationErrorResponse(BaseModel):
    """バリデーションエラーレスポンス（FastAPI標準）"""

    detail: list[dict[str, Any]]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "title"],
                            "msg": "Field required",
                            "input": {"content": "test"},
                        }
                    ]
                }
            ]
        }
    }
