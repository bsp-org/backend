"""Bible data models."""

from peewee import CharField, ForeignKeyField, IntegerField, TextField

from src.db import BaseModel


class Translation(BaseModel):
    """Bible translation/version."""

    code = CharField(max_length=10, unique=True, index=True)
    full_name = CharField(max_length=255)
    language = CharField(max_length=50)
    source_url = TextField(null=True)

    class Meta:
        table_name = "translations"


class Book(BaseModel):
    """Bible book."""

    name = CharField(max_length=50, unique=True, index=True)
    display_name = CharField(max_length=100)

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
