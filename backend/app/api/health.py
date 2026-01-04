from fastapi import APIRouter

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundError
from app.db.session import get_db


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


@router.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"result": result.scalar()}
