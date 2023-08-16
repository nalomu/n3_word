from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    nickname = Column(String)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    word_items = relationship("WordItem", back_populates="category")


class WordItem(Base):
    __tablename__ = "word_items"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True)
    pronunciation = Column(String)
    translation = Column(String)
    remark = Column(String)
    audio = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="word_items")
