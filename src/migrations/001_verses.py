"""Migration script to create the users table."""

from src.db import connect_db, close_db, database
from src.users.models import User


def main():
    """Create the users table."""
    try:
        connect_db()

        print("Creating database tables if they don't already exist...")
        database.create_tables([Translation, Verse], safe=True)

    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        close_db()


if __name__ == "__main__":
    main()
