from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.db.session import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.debug("Starting app in %s mode", settings.env)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(lambda conn: None)
    except Exception as exc:  # pragma: no cover - best effort only
        logger.warning("Database connectivity check skipped: %s", exc)
    yield
    try:
        await engine.dispose()
    except ValueError as exc:  # pragma: no cover - optional greenlet dependency missing
        if "greenlet" in str(exc):
            logger.debug("Skipping engine dispose because greenlet is unavailable")
        else:
            raise


app = FastAPI(
    title="Bible App API",
    version="0.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
