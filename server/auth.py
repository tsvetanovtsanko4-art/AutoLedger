from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .database import get_db

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

DbSession = Annotated[Session, Depends(get_db)]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": email, "exp": expire}, settings.secret_key, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> models.User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM]).get("sub")
    except jwt.InvalidTokenError:
        raise credentials_error
    if email is None:
        raise credentials_error

    user = db.scalar(select(models.User).where(models.User.email == email))
    if user is None:
        raise credentials_error
    return user


CurrentUser = Annotated[models.User, Depends(get_current_user)]
