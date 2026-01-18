from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models.article import Article
from app.db.session import get_db
from app.schemas.article import ArticleCreate, ArticleDetailResponse

router = APIRouter()


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
