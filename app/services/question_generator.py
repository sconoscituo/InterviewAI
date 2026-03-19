import json
import re
import google.generativeai as genai
from app.config import settings


def _configure():
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)


async def generate_questions(job_title: str, company: str = "", experience_years: int = 0) -> list[dict]:
    _configure()
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""면접 질문을 생성하세요.
직무: {job_title}
{"회사: " + company if company else ""}
경력: {experience_years}년

JSON:
{{"questions": [{{"id": 1, "question": "질문", "type": "behavioral|technical|situational", "tip": "답변 팁"}}]}}
10개 생성, 한국어."""
    try:
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group())["questions"]
    except Exception:
        pass
    return [
        {"id": 1, "question": f"{job_title} 직무를 선택한 이유는 무엇인가요?", "type": "behavioral", "tip": "진솔하게 동기를 설명하세요."},
        {"id": 2, "question": "본인의 강점과 약점을 말씀해 주세요.", "type": "behavioral", "tip": "약점은 개선 노력과 함께 언급하세요."},
        {"id": 3, "question": "가장 어려웠던 프로젝트 경험을 말씀해 주세요.", "type": "situational", "tip": "STAR 기법을 활용하세요."},
    ]
