"""
認証・依存関係の管理
"""

from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.redis_manager import redis_manager
from app.db.models.user import User
from app.db.session import get_db


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Cookie から session_id を抽出し、認証ユーザーを返す依存関数

    処理フロー:
    1. Cookie から session_id を抽出
    2. Redis でセッション有効性確認
    3. セッションから user_id を取得
    4. DB からユーザー情報を取得

    Args:
        request: FastAPI Request オブジェクト
        db: SQLAlchemy セッション

    Returns:
        認証済みユーザー（User）

    Raises:
        UnauthorizedError: 認証失敗時（401 Unauthorized）
            - Cookie が設定されていない
            - セッションが無効（期限切れ）
            - ユーザーが見つからない
    """
    # 1. Cookie から session_id を抽出
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise UnauthorizedError()

    # 2. Redis でセッション有効性確認
    if not redis_manager.is_session_valid(session_id):
        raise UnauthorizedError()

    # 3. セッションから user_id を取得
    session_data = redis_manager.get_session(session_id)
    if not session_data:
        raise UnauthorizedError()

    user_id = session_data.get("user_id")
    if not user_id:
        raise UnauthorizedError()

    # 4. DB からユーザー情報を取得
    user = db.query(User).filter(User.public_id == UUID(user_id)).first()
    if not user:
        raise UnauthorizedError()

    return user
