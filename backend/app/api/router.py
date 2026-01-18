from fastapi import APIRouter

from app.api.articles import router as articles_router
from app.api.health import router as health_router

api_router = APIRouter()

# 疎通確認系
api_router.include_router(
    health_router,
    prefix="",
    tags=["Health"],
)

# 記事管理
api_router.include_router(
    articles_router,
    prefix="/articles",
    tags=["articles"],
)
