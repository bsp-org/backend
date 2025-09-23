from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import get_settings
from src.db import close_db, connect_db, database

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.debug("Starting app in %s mode", settings.env)
    try:
        connect_db()
        database.execute_sql("SELECT 1")
        logger.debug("Database connection established")
    except Exception as exc:  # pragma: no cover - best effort only
        logger.warning("Database connectivity check skipped: %s", exc)
    yield
    try:
        close_db()
    except Exception as exc:  # pragma: no cover
        logger.warning("Error closing database: %s", exc)


app = FastAPI(
    title="Bible App API",
    version="0.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
