import os
import shutil

import pandas as pd
import pykakasi
from fastapi import APIRouter, UploadFile, File, Depends

import crud
import schemas
from dependencies import get_db, get_current_user
from exceptions import UnicornException
from logger import logger

router = APIRouter()


@router.post("/uploadfile/", )
async def create_upload_file(file: UploadFile = File(...), db=Depends(get_db), user=Depends(get_current_user)):
    # 验证文件类型
    content_type = file.content_type
    if content_type not in ["application/vnd.ms-excel",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        raise UnicornException('Only excel files are allowed')
    # Create a temporary file to save the uploaded content
    with open("temp_file.xlsx", "wb") as temp_file:
        shutil.copyfileobj(file.file, temp_file)

    # Read the data from the temporary file using pandas
    df = pd.read_excel("temp_file.xlsx")

    # Close and remove the temporary file
    file.file.close()
    os.remove("temp_file.xlsx")
    logger.debug(df.to_dict(orient="records"))
    # add data to Database
    counter = 0
    for index, row in df.iterrows():
        word = row.get('日语', '')
        kks = pykakasi.kakasi()

        # 构建数据字典
        data = {
            'word': row.get('日语', ''),
            'translation': row.get('中文', ''),
            'pronunciation': row.get('注音', word and ''.join([i['hira'] for i in kks.convert(word)])),
            'remark': row.get('备注', ''),
            'category_name': row.get('分类', '默认分类'),
        }
        if not data['word']:
            continue
        # 调用 CRUD 函数创建或插入单词数据到数据库
        result = crud.create_word_item_if_not_exists(db=db, word_item=schemas.WordCreate(**data))

        # 如果插入成功，增加计数器
        if result:
            counter += 1

    return schemas.StandardResponse(message=f'上传成功，共上传了{counter}条数据')
