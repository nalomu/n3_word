from datetime import timedelta, datetime
from typing import Union

from fastapi import Depends, HTTPException
from fastapi.logger import logger
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

import crud
import schemas
from database import SessionLocal

# jwt 加密用的 secret_key
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# 加密方式
ALGORITHM = "HS256"
# token过期时间
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 加密用context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 认证器
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password) -> bool:
    """
    验证密码
    :param plain_password:
    :param hashed_password:
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """
    对密码进行加密
    :param password:
    :return:
    """
    return pwd_context.hash(password)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) \
        -> Union[schemas.User, bool]:
    """
    通过jwt token获取当前用户
    :param token:
    :param db:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        logger.info('username:', username)
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(username: str, password: str, db: Session) -> Union[schemas.User, bool]:
    """
    通过账号和密码进行认证
    :param username:
    :param password:
    :param db:
    :return:
    """
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    通过data创建jwt token
    :param data:
    :param expires_delta:
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
