import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging

logger = logging.getLogger("app")


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
    )

    # --- CORS Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        show_trace = settings.debug or exc.status_code >= 500
        # ログレベルの切り分け（400系はwarning、500系はerror）
        if exc.status_code >= 500:
            logger.error(f"[{exc.error_code}] {exc.message}", exc_info=show_trace)
        else:
            logger.warning(f"[{exc.error_code}] {exc.message}", exc_info=show_trace)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    # --- Router ---
    app.include_router(api_router, prefix=settings.api_prefix)

    logger.info(
        f"Application startup | [bold green]Environment: {settings.app_env}[/bold green] | Debug: {settings.debug}",
        extra={"markup": True},
    )
    return app


app = create_app()


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # 想定外例外は必ず error + stack trace
    logger.exception("Unhandled exception occurred")

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
            }
        },
    )
