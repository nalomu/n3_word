import os
import uuid
from datetime import timedelta, datetime
from typing import Union

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from config import SECRET_KEY, ALGORITHM

# token过期时间 单位：分钟
ACCESS_TOKEN_EXPIRE_MINUTES = 1
# 30天
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

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


def create_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
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


def generate_random_filename(filename: str) -> str:
    unique_id = uuid.uuid4().hex
    base, ext = os.path.splitext(filename)
    return f"{base}_{unique_id}{ext}"
