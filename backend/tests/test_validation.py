"""
Pydantic スキーマバリデーションの単体テスト

対象:
- 記事作成・更新スキーマ（ArticleCreate, ArticleUpdate）
- 認証スキーマ（SignupRequest, LoginRequest）
- カスタムバリデータ（空白チェック、パスワード一致）
"""

import pytest
from pydantic import ValidationError

from app.schemas.article import ArticleCreate, ArticleUpdate
from app.schemas.auth import LoginRequest, SignupRequest


class TestArticleCreateValidation:
    """ArticleCreate スキーマバリデーションのテスト"""

    def test_valid_article_create(self):
        """有効な記事作成リクエストが検証を通過すること"""
        data = {
            "title": "テスト記事タイトル",
            "content": "これはテスト記事の本文です。",
            "folder_id": None,
        }
        article = ArticleCreate(**data)

        assert article.title == "テスト記事タイトル"
        assert article.content == "これはテスト記事の本文です。"
        assert article.folder_id is None

    def test_title_empty_string_fails(self):
        """タイトルが空文字列の場合に検証エラーになること"""
        data = {
            "title": "",
            "content": "本文",
        }

        with pytest.raises(ValidationError) as exc_info:
            ArticleCreate(**data)

        errors = exc_info.value.errors()
        assert any("title" in str(err["loc"]) for err in errors)

    def test_title_whitespace_only_fails(self):
        """タイトルが空白のみの場合に検証エラーになること"""
        data = {
            "title": "   ",
            "content": "本文",
        }

        with pytest.raises(ValidationError) as exc_info:
            ArticleCreate(**data)

        errors = exc_info.value.errors()
        assert any("title" in str(err["loc"]) for err in errors)
        assert any("記事タイトルを入力してください" in str(err["msg"]) for err in errors)

    def test_content_empty_string_fails(self):
        """本文が空文字列の場合に検証エラーになること"""
        data = {
            "title": "タイトル",
            "content": "",
        }

        with pytest.raises(ValidationError) as exc_info:
            ArticleCreate(**data)

        errors = exc_info.value.errors()
        assert any("content" in str(err["loc"]) for err in errors)

    def test_content_whitespace_only_fails(self):
        """本文が空白のみの場合に検証エラーになること"""
        data = {
            "title": "タイトル",
            "content": "   \n\t  ",
        }

        with pytest.raises(ValidationError) as exc_info:
            ArticleCreate(**data)

        errors = exc_info.value.errors()
        assert any("content" in str(err["loc"]) for err in errors)
        assert any("記事本文を入力してください" in str(err["msg"]) for err in errors)

    def test_title_max_length_255(self):
        """タイトルが255文字を超える場合に検証エラーになること"""
        data = {
            "title": "a" * 256,
            "content": "本文",
        }

        with pytest.raises(ValidationError) as exc_info:
            ArticleCreate(**data)

        errors = exc_info.value.errors()
        assert any("title" in str(err["loc"]) for err in errors)

    def test_folder_id_optional(self):
        """folder_id が省略可能であること"""
        data = {
            "title": "タイトル",
            "content": "本文",
        }
        article = ArticleCreate(**data)

        assert article.folder_id is None


class TestArticleUpdateValidation:
    """ArticleUpdate スキーマバリデーションのテスト"""

    def test_valid_article_update(self):
        """有効な記事更新リクエストが検証を通過すること"""
        data = {
            "title": "更新後タイトル",
            "content": "更新後本文",
            "folder_id": 1,
        }
        article = ArticleUpdate(**data)

        assert article.title == "更新後タイトル"
        assert article.content == "更新後本文"
        assert article.folder_id == 1

    def test_title_whitespace_only_fails(self):
        """タイトルが空白のみの場合に検証エラーになること"""
        data = {
            "title": "   ",
            "content": "本文",
        }

        with pytest.raises(ValidationError) as exc_info:
            ArticleUpdate(**data)

        errors = exc_info.value.errors()
        assert any("title" in str(err["loc"]) for err in errors)

    def test_content_whitespace_only_fails(self):
        """本文が空白のみの場合に検証エラーになること"""
        data = {
            "title": "タイトル",
            "content": "   ",
        }

        with pytest.raises(ValidationError) as exc_info:
            ArticleUpdate(**data)

        errors = exc_info.value.errors()
        assert any("content" in str(err["loc"]) for err in errors)


class TestSignupRequestValidation:
    """SignupRequest スキーマバリデーションのテスト"""

    def test_valid_signup_request(self):
        """有効なユーザー登録リクエストが検証を通過すること"""
        data = {
            "email": "test@example.com",
            "password": "Password123",
            "password_confirm": "Password123",
            "display_name": "テストユーザー",
        }
        signup = SignupRequest(**data)

        assert signup.email == "test@example.com"
        assert signup.password == "Password123"
        assert signup.display_name == "テストユーザー"

    def test_display_name_whitespace_only_fails(self):
        """表示名が空白のみの場合に検証エラーになること"""
        data = {
            "email": "test@example.com",
            "password": "Password123",
            "password_confirm": "Password123",
            "display_name": "   ",
        }

        with pytest.raises(ValidationError) as exc_info:
            SignupRequest(**data)

        errors = exc_info.value.errors()
        assert any("display_name" in str(err["loc"]) for err in errors)
        assert any("表示名を入力してください" in str(err["msg"]) for err in errors)

    def test_password_mismatch_fails(self):
        """パスワードと確認用パスワードが一致しない場合に検証エラーになること"""
        data = {
            "email": "test@example.com",
            "password": "Password123",
            "password_confirm": "DifferentPass456",
            "display_name": "テストユーザー",
        }

        with pytest.raises(ValidationError) as exc_info:
            SignupRequest(**data)

        errors = exc_info.value.errors()
        assert any("password_confirm" in str(err["loc"]) for err in errors)
        assert any("パスワードが一致しません" in str(err["msg"]) for err in errors)

    def test_password_min_length_8(self):
        """パスワードが8文字未満の場合に検証エラーになること"""
        data = {
            "email": "test@example.com",
            "password": "Pass1",
            "password_confirm": "Pass1",
            "display_name": "テストユーザー",
        }

        with pytest.raises(ValidationError) as exc_info:
            SignupRequest(**data)

        errors = exc_info.value.errors()
        assert any("password" in str(err["loc"]) for err in errors)

    def test_invalid_email_fails(self):
        """不正なメールアドレスの場合に検証エラーになること"""
        data = {
            "email": "invalid-email",
            "password": "Password123",
            "password_confirm": "Password123",
            "display_name": "テストユーザー",
        }

        with pytest.raises(ValidationError) as exc_info:
            SignupRequest(**data)

        errors = exc_info.value.errors()
        assert any("email" in str(err["loc"]) for err in errors)

    def test_display_name_max_length_100(self):
        """表示名が100文字を超える場合に検証エラーになること"""
        data = {
            "email": "test@example.com",
            "password": "Password123",
            "password_confirm": "Password123",
            "display_name": "a" * 101,
        }

        with pytest.raises(ValidationError) as exc_info:
            SignupRequest(**data)

        errors = exc_info.value.errors()
        assert any("display_name" in str(err["loc"]) for err in errors)


class TestLoginRequestValidation:
    """LoginRequest スキーマバリデーションのテスト"""

    def test_valid_login_request(self):
        """有効なログインリクエストが検証を通過すること"""
        data = {
            "email": "test@example.com",
            "password": "Password123",
        }
        login = LoginRequest(**data)

        assert login.email == "test@example.com"
        assert login.password == "Password123"

    def test_invalid_email_fails(self):
        """不正なメールアドレスの場合に検証エラーになること"""
        data = {
            "email": "not-an-email",
            "password": "Password123",
        }

        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)

        errors = exc_info.value.errors()
        assert any("email" in str(err["loc"]) for err in errors)

    def test_password_min_length_8(self):
        """パスワードが8文字未満の場合に検証エラーになること"""
        data = {
            "email": "test@example.com",
            "password": "short",
        }

        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)

        errors = exc_info.value.errors()
        assert any("password" in str(err["loc"]) for err in errors)

    def test_missing_fields_fail(self):
        """必須フィールドが欠けている場合に検証エラーになること"""
        # email 欠如
        with pytest.raises(ValidationError):
            LoginRequest(password="Password123")

        # password 欠如
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com")
