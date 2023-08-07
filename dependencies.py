from typing import Union

from fastapi import Depends
from jose import jwt, JWTError
from sqlalchemy.orm import Session

import crud
import schemas
from database import SessionLocal
from exceptions import UnicornException
from logger import logger
from utils import oauth2_scheme, SECRET_KEY, ALGORITHM, verify_password


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
    credentials_exception = UnicornException("Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        logger.info('username:' + username)
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
