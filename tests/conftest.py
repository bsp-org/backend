"""Pytest configuration and shared fixtures."""

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from src.main import app as _app
from src.users.models import User


@pytest.fixture
async def app():
    """Provide the FastAPI application with lifespan management."""
    async with LifespanManager(_app) as manager:
        yield manager.app


@pytest.fixture
async def client(app):
    """Provide an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture(autouse=True)
def cleanup_users():
    """Clean up users before and after each test."""
    # Clean up before test
    User.delete().execute()
    yield
    # Clean up after test
    User.delete().execute()
