"""User models."""

from datetime import datetime

from passlib.context import CryptContext
from peewee import CharField, DateTimeField, Model

from src.db import database

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BaseModel(Model):
    """Base class for Peewee models."""

    class Meta:
        database = database


class User(BaseModel):
    """User model for authentication."""

    username = CharField(max_length=50, unique=True, index=True)
    email = CharField(max_length=255, unique=True, index=True)
    password_hash = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "users"

    def set_password(self, password: str):
        """Hash and set the user's password."""
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify a password against the hash."""
        return pwd_context.verify(password, self.password_hash)

    def save(self, *args, **kwargs):
        """Update the updated_at timestamp on save."""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
