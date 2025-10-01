import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, ConfigDict

from src.config import get_settings
from src.models import Translation

logger = logging.getLogger(__name__)


class TranslationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    abbreviation: str
    full_name: str
    language: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.debug("Starting app in %s mode", settings.env)
    yield


app = FastAPI(
    title="Bible App API",
    version="0.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


# Create API router
api_router = APIRouter(prefix="/api", tags=["api"])


@api_router.get("/translations", response_model=list[TranslationResponse], tags=["translations"])
async def get_translations() -> list[TranslationResponse]:
    translations = Translation.select()
    return [TranslationResponse.model_validate(t) for t in translations]


# Include the API router in the main app
app.include_router(api_router)
