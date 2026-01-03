from fastapi import APIRouter

from app.core.exceptions import NotFoundError


router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/error-test")
def error_test():
    raise NotFoundError("test not found")


@router.get("/error-test-500")
def error_test_500():
    1 / 0
