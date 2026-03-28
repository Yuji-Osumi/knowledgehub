from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db

router = APIRouter()


@router.get(
    "/health",
    summary="ヘルスチェック",
    description="""
    API の疎通確認エンドポイントです。

    **用途**:
    - サーバーが正常に起動しているかの確認
    - ロードバランサーのヘルスチェック

    **認証**: 不要
    """,
)
def health_check():
    """API 疎通確認"""
    return {"status": "ok"}


@router.get(
    "/error-test",
    summary="エラーテスト（404）",
    description="""
    NotFoundError を発生させて、エラーレスポンス形式を確認するテスト用エンドポイントです。

    **用途**:
    - エラーハンドリングの動作確認
    - エラーレスポンス形式の検証

    **認証**: 不要

    **注意**: 開発・テスト環境でのみ使用してください。
    """,
)
def error_test():
    """404エラーテスト"""
    raise NotFoundError("test not found")


@router.get(
    "/error-test-500",
    summary="エラーテスト（500）",
    description="""
    ZeroDivisionError を発生させて、サーバーエラーレスポンスを確認するテスト用エンドポイントです。

    **用途**:
    - 想定外エラーハンドリングの動作確認
    - 500系エラーレスポンス形式の検証

    **認証**: 不要

    **注意**: 開発・テスト環境でのみ使用してください。
    """,
)
def error_test_500():
    """500エラーテスト"""
    1 / 0


@router.get(
    "/db-check",
    summary="DB接続確認",
    description="""
    データベースへの接続確認エンドポイントです。

    **用途**:
    - DB が正常に接続できるかの確認
    - DB接続プールの動作確認

    **処理**: `SELECT 1` を実行して結果を返却

    **認証**: 不要
    """,
)
def db_check(db: Session = Depends(get_db)):
    """DB接続確認"""
    result = db.execute(text("SELECT 1"))
    return {"result": result.scalar()}
