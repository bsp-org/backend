"""Bible data models."""

from peewee import CharField, ForeignKeyField, IntegerField, Model, TextField

from src.books import get_book_id, is_valid_book_name
from src.db import database


class BaseModel(Model):
    """Base class for Peewee models."""

    class Meta:
        database = database


class Translation(BaseModel):
    """Bible translation/version."""

    public_id = CharField(max_length=36, unique=True, index=True)
    abbreviation = CharField(max_length=10)
    full_name = CharField(max_length=255)
    language_code = CharField(max_length=50)
    source_url = TextField(null=True)

    class Meta:
        table_name = "translations"


class Verse(BaseModel):
    """Bible verse with support for search."""

    translation = ForeignKeyField(Translation, backref="verses", on_delete="CASCADE")
    book_id = IntegerField(index=True)
    book_name = CharField(max_length=50, index=True)
    chapter = IntegerField(index=True)
    verse = IntegerField(index=True)
    text = TextField()
    text_normalized = TextField()

    class Meta:
        table_name = "verses"
        indexes = (
            (("translation", "book_name", "chapter", "verse"), True),
            (("translation", "book_id", "chapter", "verse"), False),
            (("book_name", "chapter", "verse"), False),
        )

    def save(self, *args, **kwargs):
        """Validate book_name and set book_id before saving."""
        if not is_valid_book_name(self.book_name):
            raise ValueError(f"Invalid book name: {self.book_name}")
        # Auto-populate book_id from book_name
        self.book_id = get_book_id(self.book_name)
        return super().save(*args, **kwargs)
