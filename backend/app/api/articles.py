from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.db.models.article import Article
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.article import ArticleCreate, ArticleDetailResponse, ArticleListItem, ArticleUpdate
from app.schemas.common import ErrorResponse, ValidationErrorResponse

router = APIRouter()


@router.get(
    "",
    response_model=list[ArticleListItem],
    status_code=status.HTTP_200_OK,
    summary="記事一覧取得",
    description="""
    ログインユーザーが作成した記事の一覧を取得します。

    **認証**: Cookie の session_id が必須です。
    """,
)
def get_articles(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Article]:
    """記事一覧取得（ログインユーザーの記事のみ）"""

    query = db.query(Article).filter(
        Article.user_id == user.id,
        Article.is_valid == True,
    )

    articles = query.all()
    return articles


@router.post(
    "",
    response_model=ArticleDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="記事新規作成",
    description="""
    新しい記事を作成します。

    **必須項目**:
    - title: 記事タイトル（1〜255文字）
    - content: 記事本文（1文字以上）

    **任意項目**:
    - folder_id: フォルダID（未指定の場合は null）

    **注意**: 現在は認証未実装のため、created_by/updated_by は USER_ID=1 固定です。
    """,
    responses={
        201: {
            "description": "記事作成成功",
            "content": {
                "application/json": {
                    "example": {
                        "public_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "FastAPIの基礎",
                        "content": "FastAPIは高速なWebフレームワークです...",
                        "folder_id": None,
                        "created_at": "2026-01-28T10:00:00Z",
                        "updated_at": "2026-01-28T10:00:00Z",
                    }
                }
            },
        },
        422: {
            "description": "バリデーションエラー",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "missing",
                                "loc": ["body", "title"],
                                "msg": "Field required",
                                "input": {"content": "test"},
                            }
                        ]
                    }
                }
            },
        },
    },
)
def create_article(
    payload: ArticleCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Article:
    """
    記事新規作成
    user_id は認証ユーザーから自動設定
    """

    article = Article(
        user_id=user.id,
        title=payload.title,
        content=payload.content,
        folder_id=payload.folder_id,
        created_by=user.id,
        updated_by=user.id,
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    return article


@router.get(
    "/{public_id}",
    response_model=ArticleDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="記事詳細取得",
    description="""
    指定された public_id の記事詳細を取得します。

    **パスパラメータ**:
    - public_id: 記事のUUID（外部公開ID）

    **エラー**:
    - 404: 指定された public_id の記事が見つからない場合
    """,
    responses={
        200: {
            "description": "記事取得成功",
            "content": {
                "application/json": {
                    "example": {
                        "public_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "FastAPIの基礎",
                        "content": "FastAPIは高速なWebフレームワークです...",
                        "folder_id": None,
                        "created_at": "2026-01-28T10:00:00Z",
                        "updated_at": "2026-01-28T10:00:00Z",
                    }
                }
            },
        },
        404: {
            "description": "記事が見つかりません",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "NOT_FOUND",
                            "message": "Article with public_id xxx not found",
                            "details": None,
                        }
                    }
                }
            },
        },
    },
)
def get_article_by_id(
    public_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Article:
    """
    記事詳細取得
    public_id で検索して記事を返す
    認証ユーザーの記事のみ（is_valid=True）
    """
    article = db.query(Article).filter(
        Article.public_id == public_id,
        Article.user_id == user.id,
        Article.is_valid == True,
    ).first()

    if not article:
        raise NotFoundError(f"Article with public_id {public_id} not found")

    return article


@router.put(
    "/{public_id}",
    response_model=ArticleDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="記事更新",
    description="""
    指定された public_id の記事を更新します。

    **パスパラメータ**:
    - public_id: 記事のUUID（外部公開ID）

    **必須項目**:
    - title: 記事タイトル（1〜255文字）
    - content: 記事本文（1文字以上）

    **任意項目**:
    - folder_id: フォルダID

    **エラー**:
    - 404: 指定された public_id の記事が見つからない場合
    - 422: バリデーションエラー

    **注意**: updated_by は認証実装後に自動設定されます（現在は USER_ID=1 固定）。
    """,
    responses={
        200: {
            "description": "記事更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "public_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "FastAPIの基礎（改訂版）",
                        "content": "FastAPIは高速で使いやすいWebフレームワークです...",
                        "folder_id": None,
                        "created_at": "2026-01-28T10:00:00Z",
                        "updated_at": "2026-01-28T15:30:00Z",
                    }
                }
            },
        },
        404: {
            "description": "記事が見つかりません",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "NOT_FOUND",
                            "message": "Article with public_id xxx not found",
                            "details": None,
                        }
                    }
                }
            },
        },
        422: {
            "description": "バリデーションエラー",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "missing",
                                "loc": ["body", "title"],
                                "msg": "Field required",
                                "input": {"content": "test"},
                            }
                        ]
                    }
                }
            },
        },
    },
)
def update_article(
    public_id: UUID,
    payload: ArticleUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Article:
    """
    記事更新
    public_id で検索して記事を更新
    削除済み記事は更新不可（is_valid=True）
    """
    article = db.query(Article).filter(
        Article.public_id == public_id,
        Article.is_valid == True,
    ).first()

    if not article:
        raise NotFoundError(f"Article with public_id {public_id} not found")

    # 所有者チェック
    if article.user_id != user.id:
        raise NotFoundError(f"Article with public_id {public_id} not found")

    article.title = payload.title
    article.content = payload.content
    article.folder_id = payload.folder_id
    article.updated_by = user.id

    db.add(article)
    db.commit()
    db.refresh(article)

    return article


@router.delete(
    "/{public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="記事削除（論理削除）",
    description="""
    指定された public_id の記事を論理削除します。

    **パスパラメータ**:
    - public_id: 記事のUUID（外部公開ID）

    **動作**:
    - 記事の is_valid フラグを False に設定（物理削除はしません）
    - 削除された記事は一覧・詳細取得APIでは表示されなくなります

    **エラー**:
    - 404: 指定された public_id の記事が見つからない場合

    **レスポンス**: 204 No Content（ボディなし）
    """,
    responses={
        204: {
            "description": "記事削除成功（レスポンスボディなし）",
        },
        404: {
            "description": "記事が見つかりません",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "NOT_FOUND",
                            "message": "Article with public_id xxx not found",
                            "details": None,
                        }
                    }
                }
            },
        },
    },
)
def delete_article(
    public_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    記事削除（論理削除）
    is_valid フラグを False に設定
    削除済み記事は削除不可（is_valid=True のみ削除可）
    """
    article = db.query(Article).filter(
        Article.public_id == public_id,
        Article.is_valid == True,
    ).first()

    if not article:
        raise NotFoundError(f"Article with public_id {public_id} not found")

    # 所有者チェック
    if article.user_id != user.id:
        raise NotFoundError(f"Article with public_id {public_id} not found")

    article.is_valid = False
    article.updated_by = user.id

    db.add(article)
    db.commit()
