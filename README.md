# InterviewAI

AI 면접 코칭 서비스 - 질문 생성 + 답변 평가

## 주요 기능

- 직무/회사 입력 → Gemini AI로 예상 면접 질문 10개 생성
- 사용자 답변 입력 → AI 피드백 (논리성, 구체성, 전달력 점수)
- 모의 면접 세션 관리
- STAR 기법 코칭
- JWT 인증 + 프리미엄 플랜

## 기술 스택

- FastAPI + SQLAlchemy async + aiosqlite
- Google Gemini 1.5 Flash
- JWT 인증

## 빠른 시작

```bash
cp .env.example .env
# .env에 GEMINI_API_KEY 설정

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API 문서: http://localhost:8000/docs

## Docker

```bash
docker-compose up --build
```

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | /api/users/register | 회원가입 |
| POST | /api/users/login | 로그인 |
| GET | /api/users/me | 내 정보 |
| POST | /api/sessions | 세션 생성 + AI 질문 생성 |
| GET | /api/sessions | 세션 목록 |
| GET | /api/sessions/{id} | 세션 상세 |
| PATCH | /api/sessions/{id}/complete | 세션 완료 처리 |
| POST | /api/answers | 답변 제출 + AI 평가 |
| GET | /api/answers/session/{session_id} | 세션별 답변 목록 |
| GET | /api/answers/{id} | 답변 상세 |
| POST | /api/payments/checkout | 프리미엄 결제 시작 |
| POST | /api/payments/confirm | 결제 확인 |

## 평가 점수 항목

- **overall_score**: 종합 점수 (0~100)
- **logic_score**: 논리성
- **specificity_score**: 구체성
- **delivery_score**: 전달력
- **star_feedback**: STAR 기법 활용 평가
