"""Bible data models."""

import uuid

from peewee import CharField, ForeignKeyField, IntegerField, Model, TextField

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


class Book(BaseModel):
    """Bible book."""

    name = CharField(max_length=50, unique=True, index=True)

    class Meta:
        table_name = "books"


class Verse(BaseModel):
    """Bible verse with support for search."""

    translation = ForeignKeyField(Translation, backref="verses", on_delete="CASCADE")
    book = ForeignKeyField(Book, backref="verses", on_delete="CASCADE")
    chapter = IntegerField(index=True)
    verse = IntegerField(index=True)
    text = TextField()
    text_normalized = TextField()

    class Meta:
        table_name = "verses"
        indexes = (
            (("translation", "book", "chapter", "verse"), True),
            (("book", "chapter", "verse"), False),
        )
