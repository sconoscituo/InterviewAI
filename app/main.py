from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import users, sessions, answers, payments, voice_interview
from app.middleware.security_headers import SecurityHeadersMiddleware

app = FastAPI(
    title="InterviewAI API",
    description="AI 면접 코칭 서비스 - 질문 생성 + 답변 평가",
    version="1.0.0",
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(sessions.router)
app.include_router(answers.router)
app.include_router(payments.router)
app.include_router(voice_interview.router)


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "InterviewAI"}
