# InterviewAI - 프로젝트 설정 가이드

AI가 면접 질문을 생성하고 답변을 평가해주는 AI 면접 코칭 서비스입니다.
FastAPI 백엔드 + SQLite 기반으로 구성되어 있습니다.

---

## 1. 필요한 API 키 / 환경변수

| 환경변수 | 설명 | 발급 URL |
|---|---|---|
| `GEMINI_API_KEY` | 면접 질문 생성 및 답변 평가 AI (Google Gemini) | https://aistudio.google.com/app/apikey |
| `SECRET_KEY` | JWT 서명 비밀키 | 직접 생성 (`openssl rand -hex 32`) |
| `DATABASE_URL` | DB 연결 URL (기본값: SQLite) | 직접 구성 (프로덕션은 PostgreSQL 권장) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 액세스 토큰 만료 시간 (분, 기본값: 30) | - |
| `PREMIUM_MONTHLY_PRICE` | 프리미엄 월 구독 가격 (원, 기본값: 9900) | - |

---

## 2. GitHub Secrets 설정

GitHub 레포지토리 > **Settings > Secrets and variables > Actions > New repository secret** 에서 아래 항목을 추가합니다.

```
GEMINI_API_KEY
SECRET_KEY
DATABASE_URL
```

---

## 3. 로컬 개발 환경 설정

### 3-1. .env 파일 생성

프로젝트 루트에 `.env` 파일을 생성합니다:

```env
DATABASE_URL=sqlite+aiosqlite:///./interviewai.db
SECRET_KEY=your-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=your_gemini_api_key
PREMIUM_MONTHLY_PRICE=9900
```

### 3-2. 의존성 설치

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 4. 실행 방법

### 로컬 실행

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서: http://localhost:8000/docs

헬스체크: http://localhost:8000/health

---

## 5. 배포 방법

### Docker로 배포

```bash
docker build -t interviewai .
docker run -d -p 8000:8000 --env-file .env interviewai
```

### Docker Compose로 배포

```bash
docker compose up --build -d
```

- API 서버: http://localhost:8000
- 데이터 볼륨: `./data` 디렉토리에 마운트됩니다.

### GitHub Actions 자동 배포

`.github/workflows/ci.yml` 을 통해 `main` 브랜치에 push 시 CI가 실행됩니다.
배포 전 위의 GitHub Secrets가 모두 설정되어 있어야 합니다.
