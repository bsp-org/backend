"""API endpoints for Bible app."""

from fastapi import APIRouter, HTTPException, Query
from peewee import fn
from pydantic import BaseModel, ConfigDict

from src.books import get_book_display_name, get_book_id
from src.models import Translation, Verse
from src.text_utils import highlight_matches, normalize, remove_diacritics


# Base models for shared structures
class TranslationInfo(BaseModel):
    """Translation identification and metadata."""

    model_config = ConfigDict(from_attributes=True)

    public_id: str
    abbreviation: str
    full_name: str
    language_code: str


class BookInfo(BaseModel):
    """Book identification across all endpoints."""

    id: int
    name: str
    displan_name: str


class VerseData(BaseModel):
    """A Bible verse with complete reference and text."""

    book: BookInfo
    chapter: int
    verse: int
    text: str


# Search endpoint models
class SearchResponse(BaseModel):
    verses: list[VerseData]
    total_count: int


# Content endpoint models
class TranslationContent(BaseModel):
    translation_id: str
    verses: list[VerseData]


class ContentResponse(BaseModel):
    content: list[TranslationContent]
    total_verses: int


# Unified endpoint models
class UnifiedResponse(BaseModel):
    """Unified response for both search and content retrieval."""

    translations: list[TranslationContent]
    total_verses: int


# Metadata endpoint models
class ChapterInfo(BaseModel):
    chapter: int
    verse_count: int


class BookMetadata(BookInfo):
    """Book metadata extends BookInfo with structure details."""

    chapter_count: int
    chapters: list[ChapterInfo]


class TranslationMetadata(BaseModel):
    """Translation metadata with complete structure."""

    public_id: str
    abbreviation: str
    full_name: str
    language_code: str
    books: list[BookMetadata]
    total_books: int
    total_chapters: int
    total_verses: int


# Create API router
api_router = APIRouter(prefix="/api", tags=["api"])


@api_router.get("/translations", response_model=list[TranslationInfo], tags=["translations"])
async def get_translations() -> list[TranslationInfo]:
    translations = Translation.select()
    return [TranslationInfo.model_validate(t) for t in translations]


@api_router.get(
    "/translations/{translation_id}/metadata",
    response_model=TranslationMetadata,
    tags=["translations"],
)
async def get_translation_metadata(translation_id: str) -> TranslationMetadata:
    """
    Get complete metadata for a translation including:
    - All books with their IDs, names, and display names
    - Chapter counts per book
    - Verse counts per chapter
    - Total statistics
    """
    # Validate translation exists
    try:
        translation = Translation.get(Translation.public_id == translation_id)
    except Translation.DoesNotExist:
        raise HTTPException(status_code=404, detail="Translation not found") from None

    # Query to get chapter and verse counts grouped by book
    # This uses a single efficient query to get all metadata
    query = (
        Verse.select(
            Verse.book_id,
            Verse.book_name,
            Verse.chapter,
            fn.COUNT(Verse.id).alias("verse_count"),
        )
        .where(Verse.translation == translation)
        .group_by(Verse.book_id, Verse.book_name, Verse.chapter)
        .order_by(Verse.book_id, Verse.chapter)
    )

    # Build book metadata structure
    books_dict: dict[int, dict] = {}
    total_verses = 0
    total_chapters = 0

    for row in query:
        book_id = row.book_id
        book_name = row.book_name
        chapter = row.chapter
        verse_count = row.verse_count

        # Initialize book if not exists
        if book_id not in books_dict:
            books_dict[book_id] = {
                "book_id": book_id,
                "book_name": book_name,
                "display_book_name": get_book_display_name(
                    book_key=book_name, language=translation.language_code
                ),
                "chapters": [],
            }

        # Add chapter info
        books_dict[book_id]["chapters"].append({"chapter": chapter, "verse_count": verse_count})

        total_verses += verse_count
        total_chapters += 1

    # Convert to list and add chapter counts
    books = []
    for book_data in books_dict.values():
        book_data["chapter_count"] = len(book_data["chapters"])
        books.append(BookMetadata(**book_data))

    return TranslationMetadata(
        public_id=translation.public_id,
        abbreviation=translation.abbreviation,
        full_name=translation.full_name,
        language_code=translation.language_code,
        books=books,
        total_books=len(books),
        total_chapters=total_chapters,
        total_verses=total_verses,
    )


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
    query = Verse.select().where(Verse.translation == translation)

    if exact:
        # Exact match: search the text field with LIKE
        normalized_query = normalize(text=q, language_code=translation.language_code)
        query = query.where(Verse.text.like(f"%{normalized_query}%"))
    else:
        # Normalized search: split into words and search normalized_text
        words = [remove_diacritics(w.strip()) for w in q.split()]

        if not words:
            return SearchResponse(results=[], total_count=0)

        # Add ILIKE condition for each word (all words must match)
        for word in words:
            query = query.where(Verse.text_normalized.ilike(f"%{word}%"))

    # Execute query and build results
    verses = list(query)
    results = [
        VerseData(
            book=BookInfo(
                id=verse.book_id,
                name=verse.book_name,
                displan_name=get_book_display_name(
                    book_key=verse.book_name, language=translation.language_code
                ),
            ),
            chapter=verse.chapter,
            verse=verse.verse,
            text=highlight_matches(verse.text, q, exact=exact),
        )
        for verse in verses
    ]

    return SearchResponse(verses=results, total_count=len(results))


@api_router.get("/content", response_model=ContentResponse, tags=["content"])
async def get_content(
    translation_ids: str = Query(..., description="Comma-separated translation IDs"),
    start_book: str = Query(..., description="Starting book name"),
    start_chapter: int = Query(..., description="Starting chapter number"),
    start_verse: int | None = Query(None, description="Starting verse (None for whole chapter)"),
    end_book: str | None = Query(
        None, description="Ending book name (None for single verse/chapter)"
    ),
    end_chapter: int | None = Query(None, description="Ending chapter number"),
    end_verse: int | None = Query(None, description="Ending verse number"),
) -> ContentResponse:
    """
    Fetch Bible content with flexible range support:
    - Single verse: start_book, start_chapter, start_verse
    - Full chapter: start_book, start_chapter (no start_verse)
    - Range: start_book/chapter/verse to end_book/chapter/verse
    """
    # Parse translation IDs
    translation_id_list = [tid.strip() for tid in translation_ids.split(",")]

    # Validate translations exist
    translations = list(Translation.select().where(Translation.public_id.in_(translation_id_list)))
    if len(translations) != len(translation_id_list):
        raise HTTPException(status_code=404, detail="One or more translations not found")

    # Build the query for each translation
    content_by_translation = []
    total_verses = 0

    for translation in translations:
        query = Verse.select().where(Verse.translation == translation)

        # Determine query type and build appropriate filters
        if end_book is None and end_chapter is None and end_verse is None:
            # Single verse or chapter
            if start_verse is None:
                # Full chapter
                query = query.where(
                    (Verse.book_name == start_book) & (Verse.chapter == start_chapter)
                )
            else:
                # Single verse
                query = query.where(
                    (Verse.book_name == start_book)
                    & (Verse.chapter == start_chapter)
                    & (Verse.verse == start_verse)
                )
        else:
            # Range query - use book_id for cross-book ranges
            start_book_id = get_book_id(start_book)
            start_chapter_val = start_chapter
            start_verse_val = start_verse if start_verse is not None else 1

            end_book_val = end_book if end_book is not None else start_book
            end_book_id = get_book_id(end_book_val)
            end_chapter_val = end_chapter if end_chapter is not None else start_chapter
            end_verse_val = end_verse if end_verse is not None else 999

            # Build range condition using book_id for proper ordering
            if start_book_id == end_book_id:
                # Same book range
                if start_chapter_val == end_chapter_val:
                    # Same chapter range
                    query = query.where(
                        (Verse.book_id == start_book_id)
                        & (Verse.chapter == start_chapter_val)
                        & (Verse.verse >= start_verse_val)
                        & (Verse.verse <= end_verse_val)
                    )
                else:
                    # Different chapters in same book
                    query = query.where(
                        (Verse.book_id == start_book_id)
                        & (
                            (
                                (Verse.chapter == start_chapter_val)
                                & (Verse.verse >= start_verse_val)
                            )
                            | (
                                (Verse.chapter > start_chapter_val)
                                & (Verse.chapter < end_chapter_val)
                            )
                            | ((Verse.chapter == end_chapter_val) & (Verse.verse <= end_verse_val))
                        )
                    )
            else:
                # Different books - use book_id for proper Bible ordering
                query = query.where(
                    (
                        (Verse.book_id == start_book_id)
                        & (
                            (
                                (Verse.chapter == start_chapter_val)
                                & (Verse.verse >= start_verse_val)
                            )
                            | (Verse.chapter > start_chapter_val)
                        )
                    )
                    | ((Verse.book_id > start_book_id) & (Verse.book_id < end_book_id))
                    | (
                        (Verse.book_id == end_book_id)
                        & (
                            (Verse.chapter < end_chapter_val)
                            | ((Verse.chapter == end_chapter_val) & (Verse.verse <= end_verse_val))
                        )
                    )
                )

        # Order by natural Bible flow using book_id
        query = query.order_by(Verse.book_id, Verse.chapter, Verse.verse)

        # Get total count for first translation (all should have same count)
        if total_verses == 0:
            total_verses = query.count()

        # Execute and build results
        verses = list(query)
        content_verses = [
            VerseData(
                book=BookInfo(
                    id=verse.book_id,
                    name=verse.book_name,
                    displan_name=get_book_display_name(
                        book_key=verse.book_name, language=translation.language_code
                    ),
                ),
                chapter=verse.chapter,
                verse=verse.verse,
                text=verse.text,
            )
            for verse in verses
        ]

        content_by_translation.append(
            TranslationContent(translation_id=translation.public_id, verses=content_verses)
        )

    return ContentResponse(
        content=content_by_translation,
        total_verses=total_verses,
    )


def _apply_reference_constraints(
    query,
    start_book: str,
    start_chapter: int,
    start_verse: int | None,
    end_book: str | None,
    end_chapter: int | None,
    end_verse: int | None,
):
    """Apply reference constraints to a verse query."""
    if end_book is None and end_chapter is None and end_verse is None:
        # Single verse or chapter
        if start_verse is None:
            # Full chapter
            query = query.where((Verse.book_name == start_book) & (Verse.chapter == start_chapter))
        else:
            # Single verse
            query = query.where(
                (Verse.book_name == start_book)
                & (Verse.chapter == start_chapter)
                & (Verse.verse == start_verse)
            )
    else:
        # Range query - use book_id for cross-book ranges
        start_book_id = get_book_id(start_book)
        start_chapter_val = start_chapter
        start_verse_val = start_verse if start_verse is not None else 1

        end_book_val = end_book if end_book is not None else start_book
        end_book_id = get_book_id(end_book_val)
        end_chapter_val = end_chapter if end_chapter is not None else start_chapter
        end_verse_val = end_verse if end_verse is not None else 999

        # Build range condition using book_id for proper ordering
        if start_book_id == end_book_id:
            # Same book range
            if start_chapter_val == end_chapter_val:
                # Same chapter range
                query = query.where(
                    (Verse.book_id == start_book_id)
                    & (Verse.chapter == start_chapter_val)
                    & (Verse.verse >= start_verse_val)
                    & (Verse.verse <= end_verse_val)
                )
            else:
                # Different chapters in same book
                query = query.where(
                    (Verse.book_id == start_book_id)
                    & (
                        ((Verse.chapter == start_chapter_val) & (Verse.verse >= start_verse_val))
                        | ((Verse.chapter > start_chapter_val) & (Verse.chapter < end_chapter_val))
                        | ((Verse.chapter == end_chapter_val) & (Verse.verse <= end_verse_val))
                    )
                )
        else:
            # Different books - use book_id for proper Bible ordering
            query = query.where(
                (
                    (Verse.book_id == start_book_id)
                    & (
                        ((Verse.chapter == start_chapter_val) & (Verse.verse >= start_verse_val))
                        | (Verse.chapter > start_chapter_val)
                    )
                )
                | ((Verse.book_id > start_book_id) & (Verse.book_id < end_book_id))
                | (
                    (Verse.book_id == end_book_id)
                    & (
                        (Verse.chapter < end_chapter_val)
                        | ((Verse.chapter == end_chapter_val) & (Verse.verse <= end_verse_val))
                    )
                )
            )

    return query


def _apply_search_filters(query, q: str, exact: bool, translation: Translation):
    """Apply search filters to a verse query."""
    if exact:
        # Exact match: search the text field with LIKE
        normalized_query = normalize(text=q, language_code=translation.language_code)
        query = query.where(Verse.text.like(f"%{normalized_query}%"))
    else:
        # Normalized search: split into words and search normalized_text
        words = [remove_diacritics(w.strip()) for w in q.split()]

        if words:
            # Add ILIKE condition for each word (all words must match)
            for word in words:
                query = query.where(Verse.text_normalized.ilike(f"%{word}%"))

    return query


@api_router.get("/verses", response_model=UnifiedResponse, tags=["verses"])
async def get_verses(
    translation_ids: str = Query(..., description="Comma-separated translation IDs"),
    q: str | None = Query(
        None, description="Search query (optional, can be combined with location constraints)"
    ),
    exact: bool = Query(False, description="Use exact match searching"),
    highlight: bool | None = Query(
        None, description="Highlight matches (default: true when q is provided)"
    ),
    # Point retrieval parameters
    book: str | None = Query(None, description="Book name (for point queries)"),
    chapter: int | None = Query(None, description="Chapter number (for point queries)"),
    verse: int | None = Query(None, description="Verse number (for point queries)"),
    # Range retrieval parameters
    from_book: str | None = Query(None, description="Starting book name (for range queries)"),
    from_chapter: int | None = Query(None, description="Starting chapter (for range queries)"),
    from_verse: int | None = Query(None, description="Starting verse (for range queries)"),
    to_book: str | None = Query(None, description="Ending book name (for range queries)"),
    to_chapter: int | None = Query(None, description="Ending chapter (for range queries)"),
    to_verse: int | None = Query(None, description="Ending verse (for range queries)"),
) -> UnifiedResponse:
    """
    Unified endpoint for Bible verse retrieval with flexible filtering.

    **Features:**
    - Text search with `q` parameter (exact or normalized matching)
    - Point retrieval using `book`, `chapter`, `verse` parameters
    - Range retrieval using `from_*` and `to_*` parameters
    - Combine search with location constraints
    - Support for multiple translations
    - Optional match highlighting

    **Parameter Types (mutually exclusive):**
    - Point queries: Use `book` [+ `chapter`] [+ `verse`]
    - Range queries: Use `from_book` + `to_*` parameters

    **Examples:**
    - Search: `/api/verses?translation_ids=eng-kjv&q=love`
    - Single verse: `/api/verses?translation_ids=eng-kjv&book=john&chapter=3&verse=16`
    - Full chapter: `/api/verses?translation_ids=eng-kjv&book=john&chapter=3`
    - Full book: `/api/verses?translation_ids=eng-kjv&book=john`
    - Verse range: `/api/verses?translation_ids=eng-kjv&from_book=john&from_chapter=3&from_verse=16&to_verse=18`
    - Chapter range: `/api/verses?translation_ids=eng-kjv&from_book=john&from_chapter=3&to_chapter=5`
    - Search in chapter: `/api/verses?translation_ids=eng-kjv&book=john&chapter=3&q=love`
    - Multiple translations: `/api/verses?translation_ids=eng-kjv,spa-rvr&book=john&chapter=3&verse=16`
    """
    # Parse translation IDs
    translation_id_list = [tid.strip() for tid in translation_ids.split(",")]

    # Validate translations exist
    translations = list(Translation.select().where(Translation.public_id.in_(translation_id_list)))
    if len(translations) != len(translation_id_list):
        raise HTTPException(status_code=404, detail="One or more translations not found")

    # Detect parameter type (point vs range)
    has_point_params = book is not None or chapter is not None or verse is not None
    has_range_params = (
        from_book is not None
        or from_chapter is not None
        or from_verse is not None
        or to_book is not None
        or to_chapter is not None
        or to_verse is not None
    )

    # Validate mutually exclusive parameters
    if has_point_params and has_range_params:
        raise HTTPException(
            status_code=400,
            detail="Cannot mix point parameters (book/chapter/verse) with range parameters (from_*/to_*)",
        )

    # Convert to internal format (start_*/end_* for helper functions)
    if has_point_params:
        # Point query - treat as single point or implicit range (e.g., whole chapter/book)
        start_book = book
        start_chapter = chapter  # Keep None if not provided (for entire book)
        start_verse = verse
        end_book = None
        end_chapter = None
        end_verse = None
    elif has_range_params:
        # Range query - requires from_book and either to_* parameters or from_chapter
        if from_book is None:
            raise HTTPException(
                status_code=400,
                detail="Range queries require from_book parameter",
            )
        start_book = from_book
        start_chapter = from_chapter if from_chapter is not None else 1
        start_verse = from_verse
        end_book = to_book
        end_chapter = to_chapter
        end_verse = to_verse
    else:
        # No location constraints, only search
        start_book = None
        start_chapter = None
        start_verse = None
        end_book = None
        end_chapter = None
        end_verse = None

    # Validate that if reference constraints are provided, we have start_book
    has_reference_constraints = start_book is not None
    if q is None and not has_reference_constraints:
        raise HTTPException(
            status_code=400,
            detail="Either search query (q) or location constraints required",
        )

    # Determine highlight behavior
    should_highlight = highlight if highlight is not None else (q is not None)

    # Build the query for each translation
    content_by_translation = []
    total_verses = 0

    for translation in translations:
        query = Verse.select().where(Verse.translation == translation)

        # Apply reference constraints if provided
        if has_reference_constraints:
            if start_book is None:
                raise HTTPException(status_code=400, detail="Invalid reference constraints")

            # Special case: entire book (book without chapter)
            if start_chapter is None:
                query = query.where(Verse.book_name == start_book)
            else:
                # Use helper function for chapter/verse level constraints
                query = _apply_reference_constraints(
                    query, start_book, start_chapter, start_verse, end_book, end_chapter, end_verse
                )

        # Apply search filters if provided
        if q is not None:
            query = _apply_search_filters(query, q, exact, translation)

        # Order by natural Bible flow using book_id
        query = query.order_by(Verse.book_id, Verse.chapter, Verse.verse)

        # Get total count for first translation (all should have same count)
        if total_verses == 0:
            total_verses = query.count()

        # Execute and build results
        verses = list(query)
        content_verses = [
            VerseData(
                book=BookInfo(
                    id=verse.book_id,
                    name=verse.book_name,
                    displan_name=get_book_display_name(
                        book_key=verse.book_name, language=translation.language_code
                    ),
                ),
                chapter=verse.chapter,
                verse=verse.verse,
                text=highlight_matches(verse.text, q, exact=exact)
                if (should_highlight and q)
                else verse.text,
            )
            for verse in verses
        ]

        content_by_translation.append(
            TranslationContent(translation_id=translation.public_id, verses=content_verses)
        )

    return UnifiedResponse(
        translations=content_by_translation,
        total_verses=total_verses,
    )
