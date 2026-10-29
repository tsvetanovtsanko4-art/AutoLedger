from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from .. import models, schemas
from ..auth import CurrentUser, DbSession, create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/register", response_model=schemas.UserOut, status_code=201)
def register(user_in: schemas.UserCreate, db: DbSession):
    if db.scalar(select(models.User).where(models.User.email == user_in.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(email=user_in.email, hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=schemas.Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    user = db.scalar(select(models.User).where(models.User.email == form.username))
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user.email), "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: CurrentUser):
    return current_user
