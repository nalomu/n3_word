from typing import Union, Any

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class UserBase(BaseModel):
    nickname: str
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class Category(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class WordBase(BaseModel):
    word: str
    translation: str
    pronunciation: str
    remark: str


class WordItem(WordBase):
    category_id: int
    category: Category

    class Config:
        from_attributes = True


class WordCreate(WordBase):
    category_name: str


class StandardResponse(BaseModel):
    code: int = 200
    message: str = 'OK'
    data: Any = {}
