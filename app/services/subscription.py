from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"        # 월 9,900원
    PREMIUM = "premium" # 월 19,900원

PLAN_LIMITS = {
    PlanType.FREE:    {"sessions_per_month": 3,  "ai_feedback": False, "question_count": 5,  "model_answer": False},
    PlanType.PRO:     {"sessions_per_month": 20, "ai_feedback": True,  "question_count": 10, "model_answer": True},
    PlanType.PREMIUM: {"sessions_per_month": 99, "ai_feedback": True,  "question_count": 15, "model_answer": True},
}
PLAN_PRICES_KRW = {PlanType.FREE: 0, PlanType.PRO: 9900, PlanType.PREMIUM: 19900}
