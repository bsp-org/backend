"""Migration script to create the users table."""

from src.db import close_db, connect_db, database
from src.users.models import User


def main():
    """Create the users table."""
    try:
        connect_db()

        print("Create User table ...")
        database.create_tables([User], safe=True)

    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        close_db()


if __name__ == "__main__":
    main()
