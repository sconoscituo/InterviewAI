import json
import re
import google.generativeai as genai
from app.config import settings


def _configure():
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)


async def evaluate_answer(question: str, answer: str, job_title: str) -> dict:
    _configure()
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""면접 답변을 평가하세요.
직무: {job_title}
질문: {question}
답변: {answer}

JSON:
{{"overall_score": 85, "logic_score": 80, "specificity_score": 90, "delivery_score": 85, "strengths": ["잘한점"], "improvements": ["개선점"], "model_answer": "모범 답변 예시", "star_feedback": "STAR 기법 활용 여부 평가"}}"""
    try:
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {
        "overall_score": 0,
        "logic_score": 0,
        "specificity_score": 0,
        "delivery_score": 0,
        "strengths": [],
        "improvements": ["Gemini API 키를 설정해 주세요."],
        "model_answer": "",
        "star_feedback": "",
    }
