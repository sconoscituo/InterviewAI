import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.session import InterviewSession
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.question_generator import generate_questions

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class SessionCreate(BaseModel):
    job_title: str
    company: str = ""
    experience_years: int = 0


class SessionOut(BaseModel):
    id: int
    job_title: str
    company: str = ""
    experience_years: int
    questions: Optional[list] = None
    status: str

    class Config:
        from_attributes = True


@router.post("", response_model=SessionOut, status_code=201)
async def create_session(
    body: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    questions = await generate_questions(body.job_title, body.company, body.experience_years)
    session = InterviewSession(
        user_id=current_user.id,
        job_title=body.job_title,
        company=body.company,
        experience_years=body.experience_years,
        questions=json.dumps(questions, ensure_ascii=False),
        status="active",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    session.questions = questions
    return session


@router.get("", response_model=list[SessionOut])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.user_id == current_user.id)
    )
    sessions = result.scalars().all()
    for s in sessions:
        if s.questions:
            try:
                s.questions = json.loads(s.questions)
            except Exception:
                s.questions = []
    return sessions


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    if session.questions:
        try:
            session.questions = json.loads(session.questions)
        except Exception:
            session.questions = []
    return session


@router.patch("/{session_id}/complete", response_model=SessionOut)
async def complete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    session.status = "completed"
    await db.commit()
    await db.refresh(session)
    if session.questions:
        try:
            session.questions = json.loads(session.questions)
        except Exception:
            session.questions = []
    return session
