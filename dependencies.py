from datetime import timedelta
from typing import Union

from fastapi import Depends, HTTPException, Header, Response
from jose import jwt, JWTError
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal
from exceptions import UnicornException
from logger import logger
from utils import oauth2_scheme, SECRET_KEY, ALGORITHM, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, \
    REFRESH_TOKEN_EXPIRE_MINUTES, create_token


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(response: Response,
                           token: str = Depends(oauth2_scheme),
                           db: Session = Depends(get_db),
                           x_refresh_token: str = Header(default=None),
                           ) -> Union[models.User, bool]:
    """
    通过jwt token获取当前用户
    """
    response.headers['Access-Control-Expose-Headers'] = 'Authorization, X-Refresh-Token'
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except jwt.ExpiredSignatureError:
        logger.info("Expired signature")
        # 进行刷新令牌的验证和生成新的访问令牌
        if x_refresh_token:
            try:
                refresh_payload = jwt.decode(x_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
                refresh_username: str = refresh_payload.get("sub")
                if refresh_username is None:
                    raise HTTPException(status_code=401, detail="Invalid refresh token")

                user = crud.get_user_by_username(db, refresh_username)
                if user is None:
                    raise HTTPException(status_code=401, detail="User not found")

                # 刷新令牌
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_token(data={"sub": user.username}, expires_delta=access_token_expires)
                refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
                refresh_token = create_token(data={"sub": user.username}, expires_delta=refresh_token_expires)
                response.headers["Authorization"] = f"Bearer {access_token}"
                response.headers["X-Refresh-Token"] = refresh_token
                return user

            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Refresh token has expired")
            except jwt.JWTError:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
        else:
            raise HTTPException(status_code=401, detail="Token and refresh token both expired")

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_admin_user(user: models.User = Depends(get_current_user)):
    if not user.is_admin:
        raise UnicornException('无权限')
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
