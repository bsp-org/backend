"""Load Bible data into database."""

import json
from pathlib import Path

from src.db import database
from src.models import Book, Translation, Verse
from src.text_utils import normalize_text


def load_bible_data(json_path: str) -> None:
    """Load Bible data from JSON file into database."""
    path = Path(json_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {json_path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    abbreviation = data["abbreviation"]
    full_name = data["full_name"]
    language = data["language"]
    source_url = data.get("source_url")
    verses_data = data["verses"]

    with database.atomic():
        translation, created = Translation.get_or_create(
            abbreviation=abbreviation,
            defaults={"full_name": full_name, "language": language, "source_url": source_url},
        )

        if created:
            print(f"✓ Created translation: {abbreviation}")
        else:
            print(f"⚠ Translation {abbreviation} already exists, will add/update verses")

        book_cache = {}

        for verse_data in verses_data:
            book_name = verse_data["book"]

            if book_name not in book_cache:
                book, _ = Book.get_or_create(name=book_name)
                book_cache[book_name] = book

            book = book_cache[book_name]

            text = verse_data["text"]
            text_normalized = normalize_text(text)

            Verse.get_or_create(
                translation=translation,
                book=book,
                chapter=verse_data["chapter"],
                verse=verse_data["verse"],
                defaults={"text": text, "text_normalized": text_normalized},
            )

        print(f"✓ Loaded {len(verses_data)} verses for {abbreviation}")


def main():
    """Load all Bible versions from data directory."""
    from src.db import close_db, connect_db

    connect_db()

    print("Creating database tables if they don't already exist")
    database.create_tables([Translation, Book, Verse], safe=True)

    data_dir = Path("data")
    for json_file in data_dir.glob("*.json"):
        print(f"\nLoading {json_file.name}...")
        load_bible_data(str(json_file))

    close_db()
    print("\n✓ All Bible data loaded successfully")


if __name__ == "__main__":
    main()
