"""
セキュリティ関連機能の単体テスト

対象:
- bcrypt パスワードハッシュ化・検証
- パスワード強度検証
"""

import pytest

from app.core.security import hash_password, validate_password_strength, verify_password


class TestPasswordHashing:
    """パスワードハッシュ化・検証のテスト"""

    def test_hash_password_success(self):
        """パスワードが正常にハッシュ化されること"""
        password = "TestPassword123"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password  # 平文とは異なる
        assert len(hashed) > 0
        # bcrypt ハッシュは "$2b$" で始まる
        assert hashed.startswith("$2b$")

    def test_hash_password_different_for_same_input(self):
        """同じパスワードでも毎回異なるハッシュが生成されること（salt）"""
        password = "TestPassword123"
        hashed1 = hash_password(password)
        hashed2 = hash_password(password)

        assert hashed1 != hashed2  # salt が異なるため

    def test_hash_password_long_password(self):
        """72バイトを超えるパスワードが正常に処理されること"""
        # bcrypt は72バイトまでしか使用しない
        long_password = "a" * 100
        hashed = hash_password(long_password)

        assert hashed is not None
        assert isinstance(hashed, str)

    def test_verify_password_correct(self):
        """正しいパスワードで検証が成功すること"""
        password = "TestPassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """誤ったパスワードで検証が失敗すること"""
        password = "TestPassword123"
        wrong_password = "WrongPassword456"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """空のパスワードで検証が失敗すること"""
        password = "TestPassword123"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False

    def test_verify_password_invalid_hash(self):
        """不正なハッシュ文字列で例外が発生せず False が返ること"""
        password = "TestPassword123"
        invalid_hash = "invalid_hash_string"

        # 例外を発生させず False を返す
        assert verify_password(password, invalid_hash) is False


class TestPasswordStrength:
    """パスワード強度検証のテスト"""

    def test_valid_password(self):
        """有効なパスワードが合格すること"""
        valid_passwords = [
            "Password1",
            "Test1234",
            "Abcd1234",
            "MyP@ssw0rd",
            "SecurePass99",
        ]

        for password in valid_passwords:
            is_valid, message = validate_password_strength(password)
            assert is_valid is True, f"Failed for: {password}"
            assert message == ""

    def test_password_too_short(self):
        """8文字未満のパスワードが不合格になること"""
        short_password = "Pass1"
        is_valid, message = validate_password_strength(short_password)

        assert is_valid is False
        assert "最小 8 文字" in message

    def test_password_no_uppercase(self):
        """大文字を含まないパスワードが不合格になること"""
        password = "password123"
        is_valid, message = validate_password_strength(password)

        assert is_valid is False
        assert "大文字" in message

    def test_password_no_lowercase(self):
        """小文字を含まないパスワードが不合格になること"""
        password = "PASSWORD123"
        is_valid, message = validate_password_strength(password)

        assert is_valid is False
        assert "小文字" in message

    def test_password_no_digit(self):
        """数字を含まないパスワードが不合格になること"""
        password = "PasswordTest"
        is_valid, message = validate_password_strength(password)

        assert is_valid is False
        assert "数字" in message

    def test_password_exact_8_chars(self):
        """ちょうど8文字の有効なパスワードが合格すること"""
        password = "Pass1234"
        is_valid, message = validate_password_strength(password)

        assert is_valid is True
        assert message == ""

    def test_password_with_special_chars(self):
        """特殊文字を含むパスワードが合格すること（MVP要件外だが許容）"""
        password = "P@ssw0rd!"
        is_valid, message = validate_password_strength(password)

        assert is_valid is True
        assert message == ""
