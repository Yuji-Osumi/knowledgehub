"""
カスタム例外クラスの単体テスト

対象:
- AppException（基底クラス）
- ValidationError（400）
- UserAlreadyExistsError（400）
- UnauthorizedError（401）
- ForbiddenException（403）
- NotFoundError（404）
- ConflictError（409）
"""

import pytest

from app.core.exceptions import (
    AppException,
    ConflictError,
    ForbiddenException,
    NotFoundError,
    UnauthorizedError,
    UserAlreadyExistsError,
    ValidationError,
)


class TestAppException:
    """AppException 基底クラスのテスト"""

    def test_default_app_exception(self):
        """デフォルト引数で AppException が生成できること"""
        exc = AppException(
            message="テストエラー",
        )

        assert exc.message == "テストエラー"
        assert exc.error_code == "INTERNAL_ERROR"
        assert exc.status_code == 500
        assert exc.details is None
        assert str(exc) == "テストエラー"

    def test_app_exception_with_all_params(self):
        """全パラメータ指定で AppException が生成できること"""
        details = {"field": "email", "reason": "invalid format"}
        exc = AppException(
            message="詳細なエラー",
            error_code="CUSTOM_ERROR",
            status_code=418,
            details=details,
        )

        assert exc.message == "詳細なエラー"
        assert exc.error_code == "CUSTOM_ERROR"
        assert exc.status_code == 418
        assert exc.details == details


class TestValidationError:
    """ValidationError のテスト（400）"""

    def test_default_validation_error(self):
        """デフォルトメッセージで ValidationError が生成できること"""
        exc = ValidationError()

        assert exc.message == "Validation failed"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == 400
        assert exc.details is None

    def test_validation_error_with_custom_message(self):
        """カスタムメッセージで ValidationError が生成できること"""
        details = {"field": "title", "error": "空白のみは許可されません"}
        exc = ValidationError(
            message="タイトルのバリデーションエラー",
            details=details,
        )

        assert exc.message == "タイトルのバリデーションエラー"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == 400
        assert exc.details == details


class TestUserAlreadyExistsError:
    """UserAlreadyExistsError のテスト（400）"""

    def test_default_user_already_exists_error(self):
        """デフォルトメッセージで UserAlreadyExistsError が生成できること"""
        exc = UserAlreadyExistsError()

        assert exc.message == "メールアドレスが既に登録されています"
        assert exc.error_code == "USER_ALREADY_EXISTS"
        assert exc.status_code == 400
        assert exc.details is None

    def test_user_already_exists_error_with_details(self):
        """詳細情報付きで UserAlreadyExistsError が生成できること"""
        details = {"email": "test@example.com"}
        exc = UserAlreadyExistsError(details=details)

        assert exc.error_code == "USER_ALREADY_EXISTS"
        assert exc.status_code == 400
        assert exc.details == details


class TestUnauthorizedError:
    """UnauthorizedError のテスト（401）"""

    def test_default_unauthorized_error(self):
        """デフォルトメッセージで UnauthorizedError が生成できること"""
        exc = UnauthorizedError()

        assert exc.message == "Authentication required"
        assert exc.error_code == "UNAUTHORIZED"
        assert exc.status_code == 401
        assert exc.details is None

    def test_unauthorized_error_with_custom_message(self):
        """カスタムメッセージで UnauthorizedError が生成できること"""
        exc = UnauthorizedError(message="セッションが無効です")

        assert exc.message == "セッションが無効です"
        assert exc.error_code == "UNAUTHORIZED"
        assert exc.status_code == 401


class TestForbiddenException:
    """ForbiddenException のテスト（403）"""

    def test_default_forbidden_exception(self):
        """デフォルトメッセージで ForbiddenException が生成できること"""
        exc = ForbiddenException()

        assert exc.message == "Permission denied"
        assert exc.error_code == "FORBIDDEN"
        assert exc.status_code == 403
        assert exc.details is None

    def test_forbidden_exception_with_custom_message(self):
        """カスタムメッセージで ForbiddenException が生成できること"""
        exc = ForbiddenException(message="この記事の編集権限がありません")

        assert exc.message == "この記事の編集権限がありません"
        assert exc.error_code == "FORBIDDEN"
        assert exc.status_code == 403


class TestNotFoundError:
    """NotFoundError のテスト（404）"""

    def test_default_not_found_error(self):
        """デフォルトメッセージで NotFoundError が生成できること"""
        exc = NotFoundError()

        assert exc.message == "Resource not found"
        assert exc.error_code == "NOT_FOUND"
        assert exc.status_code == 404
        assert exc.details is None

    def test_not_found_error_with_custom_message(self):
        """カスタムメッセージで NotFoundError が生成できること"""
        details = {"resource": "article", "id": "12345"}
        exc = NotFoundError(
            message="指定された記事が見つかりません",
            details=details,
        )

        assert exc.message == "指定された記事が見つかりません"
        assert exc.error_code == "NOT_FOUND"
        assert exc.status_code == 404
        assert exc.details == details


class TestConflictError:
    """ConflictError のテスト（409）"""

    def test_default_conflict_error(self):
        """デフォルトメッセージで ConflictError が生成できること"""
        exc = ConflictError()

        assert exc.message == "Conflict occurred"
        assert exc.error_code == "CONFLICT"
        assert exc.status_code == 409
        assert exc.details is None

    def test_conflict_error_with_custom_message(self):
        """カスタムメッセージで ConflictError が生成できること"""
        exc = ConflictError(message="データの競合が発生しました")

        assert exc.message == "データの競合が発生しました"
        assert exc.error_code == "CONFLICT"
        assert exc.status_code == 409


class TestExceptionInheritance:
    """例外クラスの継承関係のテスト"""

    def test_all_exceptions_inherit_from_app_exception(self):
        """全てのカスタム例外が AppException を継承していること"""
        exceptions = [
            ValidationError(),
            UserAlreadyExistsError(),
            UnauthorizedError(),
            ForbiddenException(),
            NotFoundError(),
            ConflictError(),
        ]

        for exc in exceptions:
            assert isinstance(exc, AppException)
            assert isinstance(exc, Exception)

    def test_app_exception_inherits_from_exception(self):
        """AppException が標準の Exception を継承していること"""
        exc = AppException(message="test")
        assert isinstance(exc, Exception)
