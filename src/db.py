"""Database connection management."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from playhouse.postgres_ext import PostgresqlExtDatabase

from src.config import settings

# Create database instance
database = PostgresqlExtDatabase(
    settings.postgres_db,
    user=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    autorollback=True,
)


@asynccontextmanager
async def get_db_connection():
    """Context manager for database connections."""
    database.connect(reuse_if_open=True)
    try:
        yield database
    finally:
        if not database.is_closed():
            database.close()


async def get_session() -> AsyncGenerator[PostgresqlExtDatabase, None]:
    """FastAPI dependency that yields a database connection."""
    async with get_db_connection() as db:
        yield db


def connect_db():
    """Connect to the database."""
    database.connect(reuse_if_open=True)


def close_db():
    """Close the database connection."""
    if not database.is_closed():
        database.close()


__all__ = ["database", "get_session", "connect_db", "close_db"]
