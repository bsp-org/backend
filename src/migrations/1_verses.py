from src.db import close_db, connect_db, database
from src.models import Translation, Verse


def main():
    """Create the translation and verse tables."""
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
