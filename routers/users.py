from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud
import schemas
from exceptions import UnicornException
from utils import ACCESS_TOKEN_EXPIRE_MINUTES, create_token, REFRESH_TOKEN_EXPIRE_MINUTES
from dependencies import get_db, authenticate_user, get_current_user

router = APIRouter(prefix='/api', tags=['users'])


class UserResult(schemas.StandardResponse):
    data: schemas.User = None


@router.post("/users/", response_model=UserResult)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise UnicornException('用户名已经被使用了')
    user = crud.create_user(db=db, user=user)
    return UserResult(data=user, message='注册成功')


@router.post("/token", response_model=schemas.StandardResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise UnicornException('Incorrect username or password')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(data={"sub": user.username}, expires_delta=access_token_expires)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_token(data={"sub": user.username}, expires_delta=refresh_token_expires)
    return schemas.StandardResponse(
        data={"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"})


@router.get("/users/me", response_model=UserResult)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return UserResult(data=current_user, message='注册成功')
