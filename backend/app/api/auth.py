"""
認証関連のAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import UserAlreadyExistsError
from app.core.logging import logger
from app.core.redis_manager import redis_manager
from app.core.security import hash_password, validate_password_strength
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import SessionResponse, SignupRequest, UserResponse

router = APIRouter()


@router.post(
    "/signup",
    response_model=SessionResponse,
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
            "description": "ユーザー登録成功",
            "content": {
                "application/json": {
                    "example": {
                        "session_id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                        "user": {
                            "public_id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "user@example.com",
                            "display_name": "田中太郎",
                        },
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
    """ユーザー登録エンドポイント"""
    try:
        # 1. パスワード強度チェック
        is_valid, error_message = validate_password_strength(request.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)

        # 2. メール重複チェック
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise UserAlreadyExistsError()

        # 3. ユーザー作成
        new_user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            display_name=request.display_name,
        )

        # 4. DB 保存
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"✓ ユーザー登録成功: {new_user.email} (public_id={new_user.public_id})")

        # 5. セッション作成（Redis）
        session_id = redis_manager.create_session(
            user_id=new_user.public_id,
            ttl_hours=24,
        )

        # 6. レスポンス作成
        return SessionResponse(
            session_id=session_id,
            user=UserResponse.model_validate(new_user),
        )

    except UserAlreadyExistsError:
        db.rollback()
        raise HTTPException(status_code=400, detail="メールアドレスが既に登録されています")
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ ユーザー登録失敗: {e}")
        raise HTTPException(status_code=500, detail="ユーザー登録に失敗しました")
