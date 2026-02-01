"""
認証関連のAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.exceptions import UserAlreadyExistsError
from app.core.logging import logger
from app.core.redis_manager import redis_manager
from app.core.security import hash_password, validate_password_strength
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import SignupRequest, UserResponse

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserResponse,
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
        422: {
            "description": "バリデーションエラー",
            "content": {
                "application/json": {
                    "examples": {
                        "password_mismatch": {
                            "summary": "パスワード不一致",
                            "value": {
                                "detail": [
                                    {
                                        "type": "value_error",
                                        "loc": ["body", "password_confirm"],
                                        "msg": "Value error, パスワードが一致しません",
                                        "input": "wrong_password",
                                    }
                                ]
                            },
                        },
                        "invalid_email": {
                            "summary": "無効なメールアドレス",
                            "value": {
                                "detail": [
                                    {
                                        "type": "value_error",
                                        "loc": ["body", "email"],
                                        "msg": "value is not a valid email address",
                                        "input": "invalid-email",
                                    }
                                ]
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
            raise HTTPException(status_code=400, detail=error_message)

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
                user_id=new_user.public_id,
                ttl_hours=24,
            )
        except Exception as redis_error:
            # Redis 失敗時は DB トランザクションをロールバック
            logger.error(f"Session creation failed: {type(redis_error).__name__}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="セッション生成に失敗しました。時間をおいて再度お試しください。",
            ) from redis_error

        # 8. ユーザー情報レスポンス
        user_response = UserResponse(
            public_id=str(new_user.public_id),  # UUID を文字列に変換
            email=new_user.email,
            display_name=new_user.display_name,
        )
        response = JSONResponse(
            content=user_response.model_dump(),
        )

        # 9. Session Cookie を設定（HttpOnly, Secure, SameSite=Lax）
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,  # JavaScript からアクセス不可
            secure=True,  # HTTPS のみ（本番環境）
            samesite="lax",  # CSRF 対策
            max_age=86400,  # 24時間
            path="/",
        )

        return response

    except UserAlreadyExistsError:
        db.rollback()
        raise HTTPException(status_code=400, detail="メールアドレスが既に登録されています")
    except HTTPException:
        # DB のみロールバック
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
        raise HTTPException(status_code=500, detail="ユーザー登録に失敗しました")
