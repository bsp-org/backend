import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from src.book_names import get_book_display_name
from src.config import get_settings
from src.models import Book, Translation, Verse
from src.text_utils import normalize_text

logger = logging.getLogger(__name__)


class TranslationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: str
    abbreviation: str
    full_name: str
    language_code: str


class VerseResult(BaseModel):
    book_name: str
    chapter: int
    verse: int
    text: str


class SearchResponse(BaseModel):
    results: list[VerseResult]
    total_count: int


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


@api_router.get("/search", response_model=SearchResponse, tags=["search"])
async def search_verses(
    q: str = Query(..., description="Search query"),
    translation_id: str = Query(..., description="Public ID of the translation to search in"),
    exact: bool = Query(False, description="Use exact match searching"),
) -> SearchResponse:
    try:
        translation = Translation.get(Translation.public_id == translation_id)
    except Translation.DoesNotExist:
        raise HTTPException(status_code=404, detail="Translation not found") from None

    # Build the search query
    query = (
        Verse.select(Verse, Book.name.alias("book_name"))
        .join(Book)
        .where(Verse.translation == translation)
    )

    if exact:
        # Exact match: search the text field with LIKE
        query = query.where(Verse.text.like(f"%{q}%"))
    else:
        # Normalized search: split into words and search normalized_text
        words = [normalize_text(w.strip()) for w in q.split()]

        if not words:
            return SearchResponse(results=[], total_count=0)

        # Add ILIKE condition for each word (all words must match)
        for word in words:
            query = query.where(Verse.text_normalized.ilike(f"%{word}%"))

    # Execute query and build results
    verses = list(query)
    results = [
        VerseResult(
            book_name=get_book_display_name(
                book_key=verse.book.book_name, language=translation.language_code
            ),
            chapter=verse.chapter,
            verse=verse.verse,
            text=verse.text,
        )
        for verse in verses
    ]

    return SearchResponse(results=results, total_count=len(results))


# Include the API router in the main app
app.include_router(api_router)
