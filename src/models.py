"""Bible data models."""

import uuid

from peewee import CharField, ForeignKeyField, IntegerField, Model, TextField

from src.book_names import is_valid_book_name
from src.db import database


def tiny_uuid():
    return uuid.uuid4().hex[:8]


class BaseModel(Model):
    """Base class for Peewee models."""

    class Meta:
        database = database


class Translation(BaseModel):
    """Bible translation/version."""

    public_id = CharField(max_length=36, unique=True, index=True, default=tiny_uuid)
    abbreviation = CharField(max_length=10)
    full_name = CharField(max_length=255)
    language_code = CharField(max_length=50)
    source_url = TextField(null=True)

    class Meta:
        table_name = "translations"


class Verse(BaseModel):
    """Bible verse with support for search."""

    translation = ForeignKeyField(Translation, backref="verses", on_delete="CASCADE")
    book_name = CharField(max_length=50, index=True)
    chapter = IntegerField(index=True)
    verse = IntegerField(index=True)
    text = TextField()
    text_normalized = TextField()

    class Meta:
        table_name = "verses"
        indexes = (
            (("translation", "book_name", "chapter", "verse"), True),
            (("book_name", "chapter", "verse"), False),
        )

    def save(self, *args, **kwargs):
        """Validate book_name before saving."""
        if not is_valid_book_name(self.book_name):
            raise ValueError(f"Invalid book name: {self.book_name}")
        return super().save(*args, **kwargs)
