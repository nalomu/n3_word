import os

from gtts import gTTS

from dependencies import get_db
from models import WordItem

if __name__ == '__main__':

    db = next(get_db())
    db_items: list[WordItem] = db.query(WordItem).all()
    for db_item in db_items:
        try:
            print(f'正在生成：{db_item.id}')

            if not os.path.exists(f"static/audios"):
                os.makedirs(f"static/audios")
            # if os.path.exists(f"static/audios/word_{db_item.id}.mp3"):
            #     return schemas.StandardResponse(message='音频已存在', code=400)

            tts = gTTS(db_item.pronunciation, lang='ja')
            tts.save(f"static/audios/word_{db_item.id}.mp3")
            db_item.audio = f"/static/audios/word_{db_item.id}.mp3"
            db.commit()
        except:
            print(f'生成失败：{db_item.id}')
            pass
