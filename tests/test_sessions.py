import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine, Base


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.anyio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/users/register", json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
        })
        assert resp.status_code == 201

        resp = await client.post("/api/users/login", data={
            "username": "test@example.com",
            "password": "password123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()


@pytest.mark.anyio
async def test_create_session():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/users/register", json={
            "email": "sess@example.com",
            "password": "password123",
        })
        login = await client.post("/api/users/login", data={
            "username": "sess@example.com",
            "password": "password123",
        })
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post("/api/sessions", json={
            "job_title": "백엔드 개발자",
            "company": "테스트 회사",
            "experience_years": 2,
        }, headers=headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["job_title"] == "백엔드 개발자"
        assert data["status"] == "active"
        assert isinstance(data["questions"], list)
