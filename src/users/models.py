"""User models."""

from datetime import datetime

from peewee import BooleanField, CharField, DateTimeField, Model

from src.db import database


class BaseModel(Model):
    """Base class for Peewee models."""

    class Meta:
        database = database


class User(BaseModel):
    """User model for authentication."""

    email = CharField(max_length=255, unique=True, index=True)
    confirmed_email = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    last_login_at = DateTimeField(default=None)
    encrypt_key = CharField(max_length=128)

    class Meta:
        table_name = "users"
