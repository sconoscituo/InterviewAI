import logging
import os
import re
import json
import tempfile

import whisper
import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """Whisper STT + Gemini 기반 면접 답변 분석 서비스."""

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            logger.info("Loading Whisper base model...")
            self._model = whisper.load_model("base")
            logger.info("Whisper model loaded.")
        return self._model

    async def transcribe(self, audio_path: str) -> str:
        """음성 파일을 텍스트로 변환합니다."""
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._transcribe_sync, audio_path)
        return result

    def _transcribe_sync(self, audio_path: str) -> str:
        result = self.model.transcribe(audio_path)
        return result["text"]

    async def analyze_answer(self, question: str, transcript: str, job_title: str) -> dict:
        """
        변환된 텍스트와 질문을 Gemini로 분석합니다.

        반환 필드:
        - clarity_score: 명확성 점수 (0~100)
        - relevance_score: 관련성 점수 (0~100)
        - improvement_tip: 개선 제안 (문자열)
        """
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)

        prompt = f"""다음은 면접 음성 답변을 STT로 변환한 텍스트입니다. 평가해 주세요.

직무: {job_title}
질문: {question}
답변 (STT 변환): {transcript}

아래 JSON 형식으로만 응답하세요:
{{
  "clarity_score": 85,
  "relevance_score": 80,
  "improvement_tip": "구체적인 수치나 사례를 추가하면 더욱 설득력 있는 답변이 됩니다."
}}

- clarity_score: 답변의 명확성, 논리 구조, 문장 전달력 (0~100)
- relevance_score: 질문과의 연관성, 핵심 포인트 반영도 (0~100)
- improvement_tip: 한 문장으로 된 개선 제안"""

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")

        return {
            "clarity_score": 0,
            "relevance_score": 0,
            "improvement_tip": "Gemini API 키를 설정해 주세요.",
        }


voice_processor = VoiceProcessor()
