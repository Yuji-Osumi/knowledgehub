from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.models.article import Article
from app.db.session import get_db
from app.schemas.article import ArticleCreate, ArticleDetailResponse, ArticleListItem, ArticleUpdate

router = APIRouter()


@router.get("", response_model=list[ArticleListItem], status_code=status.HTTP_200_OK)
def get_articles(
    db: Session = Depends(get_db),
) -> list[ArticleListItem]:
    """
    記事一覧取得（暫定でユーザー別にスコープ）
    """

    # 認証未実装のため固定
    USER_ID = 1

    query = db.query(Article).filter(Article.user_id == USER_ID)

    articles = query.all()
    return articles


@router.post(
    "",
    response_model=ArticleDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_article(
    payload: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleDetailResponse:
    """
    記事新規作成
    """

    # 認証未実装のため固定
    USER_ID = 1

    article = Article(
        user_id=USER_ID,
        title=payload.title,
        content=payload.content,
        folder_id=payload.folder_id,
        created_by=USER_ID,
        updated_by=USER_ID,
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    return article


@router.get(
    "/{public_id}",
    response_model=ArticleDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_article_by_id(
    public_id: UUID,
    db: Session = Depends(get_db),
) -> ArticleDetailResponse:
    """
    記事詳細取得
    public_id で検索して記事を返す
    """
    article = db.query(Article).filter(Article.public_id == public_id).first()

    if not article:
        raise NotFoundError(f"Article with public_id {public_id} not found")

    return article


@router.put(
    "/{public_id}",
    response_model=ArticleDetailResponse,
    status_code=status.HTTP_200_OK,
)
def update_article(
    public_id: UUID,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
) -> ArticleDetailResponse:
    """
    記事更新
    public_id で検索して記事を更新
    """
    article = db.query(Article).filter(Article.public_id == public_id).first()

    if not article:
        raise NotFoundError(f"Article with public_id {public_id} not found")

    # 認証未実装のため固定
    USER_ID = 1

    article.title = payload.title
    article.content = payload.content
    article.folder_id = payload.folder_id
    article.updated_by = USER_ID

    db.add(article)
    db.commit()
    db.refresh(article)

    return article


@router.delete(
    "/{public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_article(
    public_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    """
    記事削除（論理削除）
    is_valid フラグを False に設定
    """
    article = db.query(Article).filter(Article.public_id == public_id).first()

    if not article:
        raise NotFoundError(f"Article with public_id {public_id} not found")

    # 認証未実装のため固定
    USER_ID = 1

    article.is_valid = False
    article.updated_by = USER_ID

    db.add(article)
    db.commit()
