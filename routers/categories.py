import os
import shutil

import pandas as pd
import pykakasi
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

import crud
import schemas
from dependencies import get_db, get_current_user, get_admin_user
from exceptions import UnicornException
from logger import logger
from models import Category

router = APIRouter(prefix='/api')


class CategoryListResult(schemas.StandardResponse):
    data: list[schemas.Category] = None


class CategoryResult(schemas.StandardResponse):
    data: schemas.Category = None


@router.get('/categories/', response_model=CategoryListResult)
async def get_categories(db=Depends(get_db)):
    categories = db.query(Category).all()
    return CategoryListResult(data=categories)


@router.post("/categories/", response_model=CategoryResult)
def create_category(category: schemas.Category, db: Session = Depends(get_db)):
    db_item = Category(**category.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return CategoryResult(data=db_item)


@router.get("/categories/{cid}/", response_model=CategoryResult)
def read_category(cid: int, db: Session = Depends(get_db)):
    db_item = db.query(Category).filter(Category.id == cid).first()
    if db_item is None:
        raise UnicornException("Category not found")
    return CategoryResult(data=db_item)


@router.put("/categories/{cid}/", response_model=CategoryResult)
def update_category(cid: int, category_update: schemas.Category, db: Session = Depends(get_db)):
    db_item = db.query(Category).filter(Category.id == cid).first()
    if db_item is None:
        raise UnicornException("Category not found")

    for field, value in category_update.dict().items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return CategoryResult(data=db_item)


@router.delete("/categories/{cid}/", response_model=CategoryResult)
def delete_category(cid: int, db: Session = Depends(get_db)):
    db_item = db.query(Category).filter(Category.id == cid).first()
    if db_item is None:
        raise UnicornException("Category not found")

    db.delete(db_item)
    db.commit()
    return schemas.StandardResponse(message="已删除")
