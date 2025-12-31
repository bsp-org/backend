from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health(client) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
