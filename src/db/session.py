"""Database engine and session management."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


settings = get_settings()
engine = create_async_engine(
    settings.database_dsn,
    echo=settings.debug,
    pool_pre_ping=True,
)

SessionFactory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with SessionFactory() as session:
        yield session


__all__ = ["Base", "engine", "SessionFactory", "get_session"]
