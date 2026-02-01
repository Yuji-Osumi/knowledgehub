from typing import Any, Dict, Optional


class AppException(Exception):
    """
    アプリケーション全体の基底例外クラス。
    全ての独自例外はこのクラスを継承し、共通のレスポンス形式を保持する。
    """

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message  # ユーザー向けエラーメッセージ
        self.error_code = error_code  # システム固有のエラーコード（例: NOT_FOUND）
        self.status_code = status_code  # HTTPステータスコード
        self.details = details  # エラーの具体的な詳細（バリデーション失敗箇所など）
        super().__init__(self.message)


# --- 業務例外（想定内のエラー） ---


class ValidationError(AppException):
    """400: 入力値の形式チェックなどでエラーがある場合"""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class UserAlreadyExistsError(AppException):
    """400: メールアドレスが既に登録されている場合"""

    def __init__(
        self,
        message: str = "メールアドレスが既に登録されています",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="USER_ALREADY_EXISTS",
            status_code=400,
            details=details,
        )


class UnauthorizedError(AppException):
    """401: 認証が必要なリソースに未ログインでアクセスした場合"""

    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message, error_code="UNAUTHORIZED", status_code=401, details=details
        )


class ForbiddenException(AppException):
    """403: 認可エラー（権限不足）の場合"""

    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, error_code="FORBIDDEN", status_code=403, details=details)


class NotFoundError(AppException):
    """404: 指定されたリソースが見つからない場合"""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, error_code="NOT_FOUND", status_code=404, details=details)


class ConflictError(AppException):
    """409: 重複登録など、現在のデータ状態と矛盾が起きる場合"""

    def __init__(
        self,
        message: str = "Conflict occurred",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, error_code="CONFLICT", status_code=409, details=details)
