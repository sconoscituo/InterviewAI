import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.answer import Answer
from app.models.session import InterviewSession
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.evaluator import evaluate_answer

router = APIRouter(prefix="/api/answers", tags=["answers"])


class AnswerCreate(BaseModel):
    session_id: int
    question: str
    answer_text: str


class AnswerOut(BaseModel):
    id: int
    session_id: int
    question: str
    answer_text: str
    overall_score: Optional[float] = None
    logic_score: Optional[float] = None
    specificity_score: Optional[float] = None
    delivery_score: Optional[float] = None
    strengths: Optional[list] = None
    improvements: Optional[list] = None
    model_answer: Optional[str] = None
    star_feedback: Optional[str] = None

    class Config:
        from_attributes = True


async def _verify_session(session_id: int, user_id: int, db: AsyncSession) -> InterviewSession:
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    return session


@router.post("", response_model=AnswerOut, status_code=201)
async def submit_answer(
    body: AnswerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = await _verify_session(body.session_id, current_user.id, db)
    evaluation = await evaluate_answer(body.question, body.answer_text, session.job_title)

    answer = Answer(
        session_id=body.session_id,
        question=body.question,
        answer_text=body.answer_text,
        overall_score=evaluation.get("overall_score"),
        logic_score=evaluation.get("logic_score"),
        specificity_score=evaluation.get("specificity_score"),
        delivery_score=evaluation.get("delivery_score"),
        strengths=json.dumps(evaluation.get("strengths", []), ensure_ascii=False),
        improvements=json.dumps(evaluation.get("improvements", []), ensure_ascii=False),
        model_answer=evaluation.get("model_answer"),
        star_feedback=evaluation.get("star_feedback"),
    )
    db.add(answer)
    await db.commit()
    await db.refresh(answer)

    for field in ("strengths", "improvements"):
        val = getattr(answer, field)
        if val:
            try:
                setattr(answer, field, json.loads(val))
            except Exception:
                setattr(answer, field, [])
    return answer


@router.get("/session/{session_id}", response_model=list[AnswerOut])
async def list_answers(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _verify_session(session_id, current_user.id, db)
    result = await db.execute(select(Answer).where(Answer.session_id == session_id))
    answers = result.scalars().all()
    for a in answers:
        for field in ("strengths", "improvements"):
            val = getattr(a, field)
            if val:
                try:
                    setattr(a, field, json.loads(val))
                except Exception:
                    setattr(a, field, [])
    return answers


@router.get("/{answer_id}", response_model=AnswerOut)
async def get_answer(
    answer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Answer).where(Answer.id == answer_id))
    answer = result.scalar_one_or_none()
    if not answer:
        raise HTTPException(status_code=404, detail="답변을 찾을 수 없습니다.")
    await _verify_session(answer.session_id, current_user.id, db)
    for field in ("strengths", "improvements"):
        val = getattr(answer, field)
        if val:
            try:
                setattr(answer, field, json.loads(val))
            except Exception:
                setattr(answer, field, [])
    return answer
