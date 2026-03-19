from abc import abstractmethod
from typing import List, Optional

from app.domain.ports.base_service import AbstractService


class AbstractInterviewService(AbstractService):
    """
    헥사고날 아키텍처 - 면접 서비스 포트
    면접 질문 생성 및 답변 평가 유스케이스 경계 정의
    """

    @abstractmethod
    async def generate_questions(
        self,
        job_title: str,
        company: str = "",
        experience_years: int = 0,
    ) -> List[dict]:
        """
        직무/회사/경력 정보를 받아 면접 질문 목록을 생성합니다.

        Returns:
            [{"id": int, "question": str, "type": str, "tip": str}, ...]
        """
        raise NotImplementedError

    @abstractmethod
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        job_title: str = "",
    ) -> dict:
        """
        면접 질문과 답변을 받아 AI 평가 결과를 반환합니다.

        Returns:
            {"score": int, "feedback": str, "strengths": list, "improvements": list}
        """
        raise NotImplementedError

    @abstractmethod
    async def get_session_summary(self, session_id: int) -> Optional[dict]:
        """
        면접 세션 전체 요약 및 종합 평가를 반환합니다.
        """
        raise NotImplementedError
