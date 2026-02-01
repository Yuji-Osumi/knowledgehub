"""
認証関連のAPIエンドポイント
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.exceptions import (
    AppException,
    UnauthorizedError,
    UserAlreadyExistsError,
    ValidationError,
)
from app.core.logging import logger
from app.core.redis_manager import redis_manager
from app.core.security import hash_password, validate_password_strength, verify_password
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import LoginRequest, SignupRequest, UserResponse

router = APIRouter()


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    summary="ユーザー登録",
    description="""
    新規ユーザーを登録し、セッションを開始します。

    **必須項目**:
    - email: メールアドレス（有効なメール形式）
    - password: パスワード（8文字以上、大文字・小文字・数字を含む）
    - password_confirm: パスワード確認（password と一致する必要があります）
    - display_name: 表示名（1〜50文字）

    **処理フロー**:
    1. メールアドレス形式チェック（Pydantic EmailStr）
    2. パスワード強度チェック（8文字以上、大文字・小文字・数字含む）
    3. パスワード確認チェック（password と password_confirm の一致）
    4. メール重複チェック（DB クエリ）
    5. ユーザー作成・保存（bcrypt でハッシュ化）
    6. セッション ID 生成（Redis、24時間有効）

    **セッション管理**:
    - セッション ID は Redis に保存され、24時間で自動削除されます
    - レスポンスの session_id を後続リクエストで Cookie として送信してください
    """,
    responses={
        201: {
            "description": "ユーザー登録成功（Set-Cookie ヘッダーにセッション ID を返却）",
            "content": {
                "application/json": {
                    "example": {
                        "public_id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "display_name": "田中太郎",
                    }
                }
            },
        },
        400: {
            "description": "メールアドレス重複またはパスワード強度不足",
            "content": {
                "application/json": {
                    "examples": {
                        "duplicate_email": {
                            "summary": "メールアドレス重複",
                            "value": {"detail": "メールアドレスが既に登録されています"},
                        },
                        "weak_password": {
                            "summary": "パスワード強度不足",
                            "value": {
                                "detail": "パスワードは8文字以上、大文字・小文字・数字を含む必要があります"
                            },
                        },
                    }
                }
            },
        },
        500: {
            "description": "サーバーエラー",
            "content": {"application/json": {"example": {"detail": "ユーザー登録に失敗しました"}}},
        },
    },
)
async def signup(
    request: SignupRequest,
    db: Session = Depends(get_db),
):
    """ユーザー登録エンドポイント（セッション Cookie を返却）"""
    session_id = None
    try:
        # 1. パスワード強度チェック
        is_valid, error_message = validate_password_strength(request.password)
        if not is_valid:
            raise ValidationError(message=error_message)

        # 2. メール重複チェック
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise UserAlreadyExistsError()

        # 3. ユーザー作成（仮の created_by, updated_by を設定）
        new_user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            display_name=request.display_name,
            created_by=0,  # 仮の値（後で自分のIDに更新）
            updated_by=0,
        )

        # 4. DB に追加してIDを生成
        db.add(new_user)
        db.flush()

        # 5. ID が生成されたので created_by と updated_by を更新
        new_user.created_by = new_user.id
        new_user.updated_by = new_user.id

        # 6. コミット
        db.commit()

        # 7. Redis セッション作成（DB コミット後）
        try:
            session_id = redis_manager.create_session(
                user_id=str(new_user.public_id),
                ttl_hours=24,
            )
        except Exception as redis_error:
            # Redis 失敗時は DB トランザクションをロールバック
            logger.error(f"Session creation failed: {type(redis_error).__name__}")
            db.rollback()
            raise AppException(
                message="セッション生成に失敗しました。時間をおいて再度お試しください。",
                error_code="SESSION_CREATE_FAILED",
                status_code=500,
            ) from redis_error

        # 8. ユーザー情報レスポンス
        user_response = UserResponse(
            public_id=str(new_user.public_id),  # UUID を文字列に変換
            email=new_user.email,
            display_name=new_user.display_name,
        )
        response = JSONResponse(
            content=user_response.model_dump(),
            status_code=status.HTTP_201_CREATED,
        )

        # 9. Session Cookie を設定（HttpOnly, Secure, SameSite=Lax）
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,  # JavaScript からアクセス不可
            secure=settings.SECURE_COOKIE,  # HTTPS のみ（本番環境）
            samesite="lax",  # CSRF 対策
            max_age=86400,  # 24時間
            path="/",
        )

        return response

    except UserAlreadyExistsError:
        db.rollback()
        raise
    except AppException:
        db.rollback()
        if session_id:
            try:
                redis_manager.delete_session(session_id)
            except Exception:
                pass
        raise
    except Exception as e:
        db.rollback()
        if session_id:
            try:
                redis_manager.delete_session(session_id)
            except Exception:
                pass
        logger.error(f"Signup failed: {type(e).__name__}", exc_info=True)
        raise AppException(
            message="ユーザー登録に失敗しました",
            error_code="SIGNUP_FAILED",
            status_code=500,
        )


@router.post(
    "/login",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="ログイン",
    description="""
    メールアドレスとパスワードでログインし、セッションを開始します。

    **必須項目**:
    - email: メールアドレス
    - password: パスワード

    **処理フロー**:
    1. DB からメールアドレスで検索
    2. パスワード検証（bcrypt）
    3. セッション ID 生成（Redis）
    4. Session Cookie を設定

    **セッション管理**:
    - セッション ID は HttpOnly/Secure/SameSite=lax で設定
    - 24時間有効です
    """,
    responses={
        200: {
            "description": "ログイン成功（Set-Cookie ヘッダーにセッション ID を返却）",
            "content": {
                "application/json": {
                    "example": {
                        "public_id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "display_name": "田中太郎",
                    }
                }
            },
        },
        401: {
            "description": "認証失敗（メール未検出またはパスワード不一致）",
            "content": {"application/json": {"example": {"detail": "Invalid email or password"}}},
        },
        500: {
            "description": "サーバーエラー",
            "content": {"application/json": {"example": {"detail": "ログインに失敗しました"}}},
        },
    },
)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """ログインエンドポイント（セッション Cookie を返却）"""
    session_id = None
    try:
        # 1. DB からメールアドレスで検索
        user = db.query(User).filter(User.email == request.email).first()

        # 2. パスワード検証（ユーザー存在有無を隠すため、不一致の場合と同じエラー）
        if not user or not verify_password(request.password, user.password_hash):
            raise UnauthorizedError(message="Invalid email or password")

        # 3. Redis セッション作成
        try:
            session_id = redis_manager.create_session(
                user_id=str(user.public_id),
                ttl_hours=24,
            )
        except Exception as redis_error:
            logger.error(f"Session creation failed: {type(redis_error).__name__}")
            raise AppException(
                message="セッション生成に失敗しました。時間をおいて再度お試しください。",
                error_code="SESSION_CREATE_FAILED",
                status_code=500,
            ) from redis_error

        # 4. ユーザー情報レスポンス
        user_response = UserResponse(
            public_id=str(user.public_id),
            email=user.email,
            display_name=user.display_name,
        )
        response = JSONResponse(content=user_response.model_dump())

        # 5. Session Cookie を設定
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=settings.SECURE_COOKIE,
            samesite="lax",
            max_age=86400,
            path="/",
        )

        return response

    except AppException:
        if session_id:
            try:
                redis_manager.delete_session(session_id)
            except Exception:
                pass
        raise
    except Exception as e:
        if session_id:
            try:
                redis_manager.delete_session(session_id)
            except Exception:
                pass
        logger.error(f"Login failed: {type(e).__name__}", exc_info=True)
        raise AppException(
            message="ログインに失敗しました",
            error_code="LOGIN_FAILED",
            status_code=500,
        )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ログアウト",
    description="""
    セッションを終了して、Cookie をクリアします。

    **処理フロー**:
    1. Cookie から session_id を抽出
    2. Redis からセッションを削除
    3. Browser の Cookie をクリア（Max-Age=0）
    4. キャッシュコントロールヘッダを設定

    **レスポンス**:
    - 204 No Content（ボディなし）
    - Set-Cookie ヘッダで session_id をクリア
    """,
    responses={
        204: {
            "description": "ログアウト成功（Cookie クリア）",
        },
        401: {
            "description": "認証なし（Cookie が設定されていない場合）",
            "content": {"application/json": {"example": {"detail": "Unauthorized"}}},
        },
    },
)
async def logout(
    request: Request,
    redis_manager_instance=Depends(lambda: redis_manager),
):
    """ログアウトエンドポイント（セッション Cookie をクリア）"""
    try:
        # 1. Cookie から session_id を抽出
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise UnauthorizedError()

        # 2. Redis からセッションを削除
        try:
            redis_manager.delete_session(session_id)
        except Exception as redis_error:
            logger.error(f"Session deletion failed: {type(redis_error).__name__}")
            # Redis エラーでもログアウト可能（Cookie は削除される）

        # 3. Cookie をクリア + キャッシュコントロール
        response = JSONResponse(content=None, status_code=204)
        response.delete_cookie(
            key="session_id",
            httponly=True,
            secure=settings.SECURE_COOKIE,
            samesite="lax",
            path="/",
        )

        # キャッシュコントロールヘッダ
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response

    except AppException:
        raise
    except Exception as e:
        logger.error(f"Logout failed: {type(e).__name__}", exc_info=True)
        raise AppException(
            message="ログアウトに失敗しました",
            error_code="LOGOUT_FAILED",
            status_code=500,
        )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="現在のユーザー情報取得",
    description="""
    セッション Cookie から認証ユーザーの情報を取得します。

    **処理フロー**:
    1. Cookie から session_id を抽出
    2. Redis でセッション有効性確認
    3. セッションから user_id を取得
    4. DB からユーザー情報を取得

    **認証**:
    - Cookie の session_id が必須
    - セッションは 24 時間で自動期限切れ
    """,
    responses={
        200: {
            "description": "ユーザー情報取得成功",
            "content": {
                "application/json": {
                    "example": {
                        "public_id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "display_name": "田中太郎",
                    }
                }
            },
        },
        401: {
            "description": "認証失敗（Cookie 未設定またはセッション期限切れ）",
            "content": {"application/json": {"example": {"detail": "Unauthorized"}}},
        },
        500: {
            "description": "サーバーエラー",
            "content": {
                "application/json": {"example": {"detail": "ユーザー情報取得に失敗しました"}}
            },
        },
    },
)
async def get_me(
    user: User = Depends(get_current_user),
):
    """現在のユーザー情報取得エンドポイント"""
    return UserResponse(
        public_id=str(user.public_id),
        email=user.email,
        display_name=user.display_name,
    )
