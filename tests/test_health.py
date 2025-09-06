from __future__ import annotations

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health() -> None:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
