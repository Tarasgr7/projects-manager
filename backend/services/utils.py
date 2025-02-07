
from ..dependencies import SessionLocal,logger
from typing import Annotated
from fastapi import Depends,HTTPException,status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..services.auth_service import get_current_user

def get_db():
  db= SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency=Annotated[Session,Depends(get_db)]


user_dependency=Annotated[dict,Depends(get_current_user)]



bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')


def raise_error(detail: str, status_code: int):
    logger.error(detail)
    raise HTTPException(status_code=status_code, detail=detail)