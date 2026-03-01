"""
認証関連のリクエスト/レスポンス スキーマ
"""

from pydantic import BaseModel, EmailStr, Field, field_validator


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

    @field_validator("display_name")
    @classmethod
    def display_name_not_empty(cls, display_name):
        """display_nameが空白のみでないことを検証"""
        if not display_name.strip():
            raise ValueError("表示名を入力してください")
        return display_name

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, password_confirm, info):
        """password と password_confirm が一致するか検証"""
        password = info.data.get("password")
        if password and password_confirm != password:
            raise ValueError("パスワードが一致しません")
        return password_confirm


class UserResponse(BaseModel):
    """ユーザー情報レスポンス"""

    public_id: str = Field(..., description="ユーザー公開 ID（UUID）")
    email: str = Field(..., description="メールアドレス")
    display_name: str = Field(..., description="表示名")

    model_config = {"from_attributes": True}


class SessionResponse(BaseModel):
    """セッション作成レスポンス"""

    session_id: str = Field(..., description="セッション ID")
    user: UserResponse = Field(..., description="ユーザー情報")
