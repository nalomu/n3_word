from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
import schemas
import dependencies as deps

router = APIRouter(prefix='/api', tags=['feedbacks'])


class FeedbackList(schemas.StandardResponse):
    data: list[schemas.Feedback]


class FeedbackResult(schemas.StandardResponse):
    data: schemas.Feedback


@router.get('/feedbacks', response_model=FeedbackList)
async def get_feedbacks(_user: models.User = Depends(deps.get_admin_user), db: Session = Depends(deps.get_db)):
    feedbacks = db.query(models.Feedback).all()
    return FeedbackList(data=feedbacks)


class ReviewFeedbackRequest(BaseModel):
    status: str


@router.post('/feedbacks/{feedback_id}', response_model=FeedbackResult)
async def review_feedback(feedback_id: int,
                          data: ReviewFeedbackRequest,
                          _user: models.User = Depends(deps.get_admin_user),
                          db: Session = Depends(deps.get_db)):
    feedback: models.Feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if feedback is None:
        return schemas.StandardResponse(message='未找到记录', code=400)
    feedback.status = 'success' if data.status == 'success' else 'error'
    if feedback.status != 'error':
        if feedback.error_type == 'pronunciation':
            feedback.word.audio = feedback.audio_url
        else:
            feedback.word.translation = feedback.translate
        db.add(feedback.word)
    db.commit()
    db.refresh(feedback)
    return FeedbackResult(data=feedback)
