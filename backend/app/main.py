from fastapi import FastAPI

from app.core.config import settings
from app.api.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )

    # API ルーティング登録
    app.include_router(api_router)

    return app


app = create_app()
