"""Load Bible data into database."""

import json
from pathlib import Path

from src.book_names import get_book_id
from src.db import database
from src.models import Translation, Verse
from src.text_utils import normalize, remove_diacritics


def load_bible_data(json_path: str) -> None:
    """Load Bible data from JSON file into database."""
    path = Path(json_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {json_path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    abbreviation = data["abbreviation"]
    full_name = data["full_name"]
    language_code = data["language_code"]
    source_url = data.get("source_url")
    verses_data = data["verses"]

    with database.atomic():
        translation, created = Translation.get_or_create(
            abbreviation=abbreviation,
            full_name=full_name,
            language_code=language_code,
            defaults={
                "full_name": full_name,
                "language_code": language_code,
                "source_url": source_url,
            },
        )

        if created:
            print(f"✓ Created translation: {abbreviation}")
        else:
            print(f"⚠ Translation {abbreviation} already exists, will add/update verses")

        # Process verses in batches
        batch_size = 1000
        total_verses = len(verses_data)

        for i in range(0, total_verses, batch_size):
            batch = verses_data[i : i + batch_size]

            # Prepare verse data for bulk insert
            verse_records = []
            for verse_data in batch:
                raw_text = verse_data["text"]
                text = normalize(text=raw_text, language_code=language_code)
                text_normalized = remove_diacritics(text=text)
                book_name = verse_data["book"]

                verse_records.append(
                    {
                        "translation": translation.id,
                        "book_id": get_book_id(book_name),
                        "book_name": book_name,
                        "chapter": verse_data["chapter"],
                        "verse": verse_data["verse"],
                        "text": text,
                        "text_normalized": text_normalized,
                    }
                )

            # Bulk insert verses (skip duplicates)
            try:
                Verse.insert_many(verse_records).on_conflict_ignore().execute()
            except Exception as e:
                # Fallback to individual inserts if bulk insert fails
                print(f"Bulk insert failed, falling back to individual inserts: {e}")
                for record in verse_records:
                    Verse.get_or_create(
                        translation=record["translation"],
                        book_name=record["book_name"],
                        chapter=record["chapter"],
                        verse=record["verse"],
                        defaults={
                            "book_id": record["book_id"],
                            "text": record["text"],
                            "text_normalized": record["text_normalized"],
                        },
                    )

            print(f"  Processed {min(i + batch_size, total_verses)}/{total_verses} verses")

        print(f"✓ Loaded {len(verses_data)} verses for {abbreviation}")


def main():
    """Load all Bible versions from data directory."""
    from src.db import close_db, connect_db

    connect_db()

    print("Creating database tables if they don't already exist")
    database.create_tables([Translation, Verse], safe=True)

    data_dir = Path("data")
    for json_file in data_dir.glob("*.json"):
        print(f"\nLoading {json_file.name}...")
        load_bible_data(str(json_file))

    close_db()
    print("\n✓ All Bible data loaded successfully")


if __name__ == "__main__":
    main()
