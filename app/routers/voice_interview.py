import logging
import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.session import InterviewSession
from app.models.user import User
from app.services.voice_processor import voice_processor
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/voice", tags=["voice-interview"])

ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/mp4",
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "video/webm",  # webm은 video/* MIME으로도 올 수 있음
}


class AnalyzeAnswerRequest(BaseModel):
    question: str
    transcript: str
    job_title: str = "일반"


class TranscribeResponse(BaseModel):
    transcript: str
    filename: str


class AnalyzeAnswerResponse(BaseModel):
    question: str
    transcript: str
    clarity_score: int
    relevance_score: int
    improvement_tip: str


class VoiceSessionRecord(BaseModel):
    session_id: int
    job_title: str
    company: str
    status: str
    questions: list | None = None

    class Config:
        from_attributes = True


@router.post("/transcribe", response_model=TranscribeResponse, summary="음성 파일 → 텍스트 변환 (Whisper STT)")
async def transcribe_audio(
    file: UploadFile = File(..., description="음성 파일 (webm, mp4, wav)"),
    current_user: User = Depends(get_current_user),
):
    """
    업로드된 음성 파일을 Whisper STT로 텍스트로 변환합니다.

    - 지원 포맷: webm, mp4, wav, mpeg
    - 반환: 변환된 텍스트(transcript)
    """
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다: {file.content_type}. (webm/mp4/wav 지원)",
        )

    suffix_map = {
        "audio/webm": ".webm",
        "video/webm": ".webm",
        "audio/mp4": ".mp4",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/mpeg": ".mp3",
    }
    suffix = suffix_map.get(file.content_type, ".webm")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        transcript = await voice_processor.transcribe(tmp_path)
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"STT 변환 중 오류가 발생했습니다: {str(e)}")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    return TranscribeResponse(transcript=transcript, filename=file.filename or "")


@router.post(
    "/analyze-answer",
    response_model=AnalyzeAnswerResponse,
    summary="STT 텍스트 + 질문 → Gemini 답변 분석",
)
async def analyze_answer(
    body: AnalyzeAnswerRequest,
    current_user: User = Depends(get_current_user),
):
    """
    STT로 변환된 텍스트와 질문을 Gemini AI로 분석합니다.

    - clarity_score: 명확성 점수 (0~100)
    - relevance_score: 관련성 점수 (0~100)
    - improvement_tip: 개선 제안
    """
    result = await voice_processor.analyze_answer(
        question=body.question,
        transcript=body.transcript,
        job_title=body.job_title,
    )
    return AnalyzeAnswerResponse(
        question=body.question,
        transcript=body.transcript,
        clarity_score=result.get("clarity_score", 0),
        relevance_score=result.get("relevance_score", 0),
        improvement_tip=result.get("improvement_tip", ""),
    )


@router.get(
    "/sessions/{session_id}",
    response_model=VoiceSessionRecord,
    summary="음성 면접 세션 기록 조회",
)
async def get_voice_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    특정 면접 세션의 기록을 반환합니다.
    음성 면접 시 사용한 세션 정보를 확인할 수 있습니다.
    """
    import json

    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    questions = []
    if session.questions:
        try:
            questions = json.loads(session.questions)
        except Exception:
            questions = []

    return VoiceSessionRecord(
        session_id=session.id,
        job_title=session.job_title,
        company=session.company or "",
        status=session.status,
        questions=questions,
    )
