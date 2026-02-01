"""
認証関連のリクエスト/レスポンス スキーマ
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """ログインリクエスト"""

    email: EmailStr = Field(..., description="ユーザーメール")
    password: str = Field(..., min_length=8, description="パスワード")


class SignupRequest(BaseModel):
    """ユーザー登録リクエスト"""

    email: EmailStr = Field(..., min_length=1, description="ユーザーメール")
    password: str = Field(..., min_length=8, description="パスワード")
    password_confirm: str = Field(..., min_length=8, description="パスワード（確認）")
    display_name: str = Field(..., min_length=1, max_length=100, description="表示名")


class UserResponse(BaseModel):
    """ユーザー情報レスポンス"""

    public_id: str = Field(..., description="ユーザー公開 ID（UUID）")
    email: str = Field(..., description="メールアドレス")
    display_name: str = Field(..., description="表示名")

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    """セッション作成レスポンス"""

    session_id: str = Field(..., description="セッション ID")
    user: UserResponse = Field(..., description="ユーザー情報")
