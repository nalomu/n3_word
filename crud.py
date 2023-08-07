from typing import Union

from sqlalchemy.orm import Session, joinedload

import models
import schemas
from utils import get_password_hash


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(nickname=user.nickname, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_word_item_if_not_exists(db: Session, word_item: schemas.WordCreate) -> Union[models.WordItem, bool]:
    db_word_item = db.query(models.WordItem).filter(models.WordItem.word == word_item.word).first()
    if db_word_item:
        return False
    category = db.query(models.Category).filter(models.Category.name == word_item.category_name).first()
    if not category:
        category = models.Category(name=word_item.category_name)
        db.add(category)
        db.commit()
        db.refresh(category)
    db_word_item = models.WordItem(
        word=word_item.word,
        translation=word_item.translation,
        pronunciation=word_item.pronunciation,
        remark=word_item.remark,
        category_id=category.id,
    )
    db.add(db_word_item)
    db.commit()
    db.refresh(db_word_item)
    return db_word_item


def get_words(db: Session, ):
    return (db.query(models.WordItem)
            .options(joinedload(models.WordItem.category))
            # .offset(skip)
            # .limit(limit)
            .all())
