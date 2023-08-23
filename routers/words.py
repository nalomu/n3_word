import os
import shutil
import tempfile

import magic
import pandas as pd
import pykakasi
from fastapi import APIRouter, UploadFile, File, Depends, Form
from gtts import gTTS
from pydantic import BaseModel
from pydub import AudioSegment
from sqlalchemy.orm import Session, joinedload

import crud
import schemas
from dependencies import get_db, get_admin_user, get_current_user
from exceptions import UnicornException
from logger import logger
from models import WordItem, User, Feedback
from utils import generate_random_filename

router = APIRouter(prefix='/api')


@router.post("/uploadfile/", )
async def create_upload_file(file: UploadFile = File(...), db=Depends(get_db), admin=Depends(get_admin_user)):
    # 验证文件类型
    content_type = file.content_type
    if content_type not in ["application/vnd.ms-excel",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        raise UnicornException('仅允许上传excel文件')
    if file.size > 1024 * 1024 * 10:
        raise UnicornException('文件大小不能超过10MB')
    # Create a temporary file to save the uploaded content
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate a random filename to save the uploaded file
        temp_file_name = os.path.join(temp_dir, generate_random_filename(file.filename))
        with open(temp_file_name, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            # Read the data from the temporary file using pandas
            df = pd.read_excel(temp_file_name)

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


class WordsResponse(schemas.StandardResponse):
    data: list[schemas.WordItem]


class WordResponse(schemas.StandardResponse):
    data: schemas.WordItem


class WordRange(BaseModel):
    type: str = ''
    range: list[int] = []


class WordListQuery(BaseModel):
    question_range: WordRange = WordRange()
    question_count: int = 40


@router.get('/words', response_model=WordsResponse)
async def get_words(db=Depends(get_db)):
    words = crud.get_words(db=db)
    return schemas.StandardResponse(data=words)


@router.post('/wordsList', response_model=WordsResponse)
async def get_words_list(word_range: WordListQuery = WordListQuery(), db=Depends(get_db)):
    query = (db.query(WordItem)
             .options(joinedload(WordItem.category))
             )
    if len(word_range.question_range.range) > 0:
        if word_range.question_range.type == 'category':
            query = query.filter(WordItem.category_id.in_(word_range.question_range.range))
        else:
            query = query.filter(WordItem.id.in_(word_range.question_range.range))
    if word_range.question_count > 0:
        query = query.limit(word_range.question_count)
    words = query.all()
    return schemas.StandardResponse(data=words)


@router.post("/words/", response_model=WordResponse)
def create_word_item(word_item: schemas.WordCreateC, db: Session = Depends(get_db), _user=Depends(get_admin_user)):
    db_item = WordItem(**word_item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return WordResponse(data=db_item)


@router.get("/words/{word_id}/", response_model=WordResponse)
def read_word_item(word_id: int, db: Session = Depends(get_db)):
    db_item = db.query(WordItem).filter(WordItem.id == word_id).first()
    if db_item is None:
        raise UnicornException("Word item not found")
    return schemas.StandardResponse(data=db_item)


@router.put("/words/{word_id}/", response_model=WordResponse)
def update_word_item(word_id: int, word_item_update: schemas.WordCreateC, db: Session = Depends(get_db),
                     _user=Depends(get_admin_user)):
    db_item = db.query(WordItem).filter(WordItem.id == word_id).first()
    if db_item is None:
        raise UnicornException("Word item not found")

    for field, value in word_item_update.dict().items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return WordResponse(data=db_item)


@router.delete("/words/{word_id}/", response_model=schemas.StandardResponse)
def delete_word_item(word_id: int, db: Session = Depends(get_db), _user=Depends(get_admin_user)):
    db_item = db.query(WordItem).filter(WordItem.id == word_id).first()
    if db_item is None:
        raise UnicornException("Word item not found")

    db.delete(db_item)
    db.commit()
    return schemas.StandardResponse(message='删除成功')


@router.get('/words/{word_id}/audio/', response_model=schemas.StandardResponse)
async def get_word_audio(word_id: int, db: Session = Depends(get_db), _user=Depends(get_admin_user)):
    db_item: WordItem = db.query(WordItem).filter(WordItem.id == word_id).first()
    if db_item is None:
        raise UnicornException("Word item not found")

    if not os.path.exists(f"static/audios"):
        os.makedirs(f"static/audios")
    # if os.path.exists(f"static/audios/word_{db_item.id}.mp3"):
    #     return schemas.StandardResponse(message='音频已存在', code=400)

    tts = gTTS(db_item.word, lang='ja')
    tts.save(f"static/audios/word_{db_item.id}.mp3")
    db_item.audio = f"/static/audios/word_{db_item.id}.mp3"
    db.commit()
    return schemas.StandardResponse(message='生成成功')


@router.post('/words/{word_id}/feedback/', response_model=schemas.StandardResponse)
async def word_feedback(word_id: int,
                        file: UploadFile = File(default=None),
                        db: Session = Depends(get_db),
                        error_type: str = Form(),
                        translate: str = Form(default=None),
                        user: User = Depends(get_current_user)):
    db_item: WordItem = db.query(WordItem).filter(WordItem.id == word_id).first()
    if db_item is None:
        raise UnicornException("没有找到这个单词")
    if not os.path.exists(f"static/audios"):
        os.makedirs(f"static/audios")
    feedback: Feedback = db.query(Feedback).filter(
        (Feedback.user_id == user.id)
        & (Feedback.word_id == db_item.id)
        & (Feedback.error_type == error_type)
    ).first()
    if not feedback:
        feedback = Feedback(user_id=user.id, word_id=db_item.id, error_type=error_type)
    if error_type == 'pronunciation':
        if file is None:
            return schemas.StandardResponse(message='请上传音频', code=400)
        print(file.headers)
        mime_type = magic.Magic()
        file_mime = mime_type.from_buffer(file.file.read())
        logger.info(f'file_mime:{file_mime}', )
        file.file.seek(0)

        # 将 WAV 文件加载为 AudioSegment 对象
        # if not file_mime.startswith('WebM'):
        #     return schemas.StandardResponse(message='上传格式错误', code=400)
        wav_file = f"static/audios/word_{db_item.id}_{user.id}.wav"
        audio_url = f"static/audios/word_{db_item.id}_{user.id}.mp3"
        try:
            with open(wav_file, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            audio = AudioSegment.from_file(wav_file)
            audio.export(audio_url, format="mp3")
        except Exception as e:
            logger.exception('出错了：')
            return schemas.StandardResponse(message='上传格式错误,请重新选择', code=400)
        feedback.audio_url = audio_url
    else:
        feedback.translate = translate
    feedback.status = 'pending'
    db.add(feedback)
    db.commit()
    return schemas.StandardResponse(message='上传成功')
