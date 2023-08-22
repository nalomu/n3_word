from typing import Union, Any, Optional

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
    is_admin: int

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str


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
    audio: Union[str, None] = None


class WordItem(WordBase):
    id: int
    category_id: int
    category: Category

    class Config:
        from_attributes = True


class WordCreate(WordBase):
    category_name: str


class WordCreateC(WordBase):
    category_id: int


class StandardResponse(BaseModel):
    code: int = 200
    message: str = 'OK'
    data: Any = {}


class FeedbackBase(BaseModel):
    audio_url: Optional[str] = ''
    error_type: str = ''
    translate: Optional[str] = ''
    status: str = ''


class Feedback(FeedbackBase):
    id: int
    user_id: int = None
    user: User = None
    word_id: int = None
    word: WordItem = None

    class Config:
        from_attributes = True
