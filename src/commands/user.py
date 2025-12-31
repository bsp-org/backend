"""CLI commands for the Bible app."""

import sys

import click
from peewee import IntegrityError

from src.db import close_db, connect_db, database
from src.users.models import User


@click.group()
def cli():
    """Bible app CLI commands."""
    pass


@cli.command()
@click.option("--username", prompt=True, help="Username for the new user")
@click.option("--email", prompt=True, help="Email for the new user")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password for the new user")
def create_user(username: str, email: str, password: str):
    """Create a new user."""
    try:
        # Connect to database
        connect_db()

        # Create users table if it doesn't exist
        database.create_tables([User], safe=True)

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()

        click.echo(f"User '{username}' created successfully with ID: {user.id}")
    except IntegrityError as e:
        error_msg = str(e).lower()
        if "username" in error_msg:
            click.echo(f"Error: Username '{username}' already exists", err=True)
        elif "email" in error_msg:
            click.echo(f"Error: Email '{email}' already exists", err=True)
        else:
            click.echo(f"Error: User already exists - {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error creating user: {e}", err=True)
        sys.exit(1)
    finally:
        close_db()


if __name__ == "__main__":
    cli()
