import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        reg = await client.post("/api/v1/auth/register", json={
            "email": "engineer@dataforge.com",
            "password": "eng123",
            "full_name": "Data Engineer",
            "role": "ENGINEER",
        })
        assert reg.status_code == 201

        login = await client.post("/api/v1/auth/login", json={
            "email": "engineer@dataforge.com",
            "password": "eng123",
        })
        assert login.status_code == 200
        assert "access_token" in login.json()
