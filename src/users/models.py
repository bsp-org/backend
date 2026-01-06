"""User models."""

import base64
import secrets
from datetime import datetime

from cryptography.fernet import Fernet
from peewee import BooleanField, CharField, DateTimeField, Model

from src.db import database


def generate_encrypt_key() -> str:
    """Generate a random encryption key for AES-256 (32 bytes), base64-encoded."""
    return Fernet.generate_key().decode()


class BaseModel(Model):
    """Base class for Peewee models."""

    class Meta:
        database = database


class User(BaseModel):
    """User model for authentication."""

    email = CharField(max_length=255, unique=True, index=True)
    confirmed_email = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    last_login_at = DateTimeField(default=None, null=True)
    encrypt_key = CharField(max_length=128, default=generate_encrypt_key)

    class Meta:
        table_name = "users"
