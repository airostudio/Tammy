"""Tests for API endpoints"""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
class TestAPI:
    """Test API endpoints"""

    async def test_root(self):
        """Test root endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            assert "message" in response.json()

    async def test_health_check(self):
        """Test health check endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    async def test_info(self):
        """Test info endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/info")
            assert response.status_code == 200
            assert "features" in response.json()

    async def test_chat_capabilities(self):
        """Test chat capabilities endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/chat/capabilities")
            assert response.status_code == 200
            data = response.json()
            assert "capabilities" in data
            assert "examples" in data
