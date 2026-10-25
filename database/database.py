import sqlite3
from pathlib import Path

# Store the database in the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "novatrip.db"


def get_connection():
    """Create a connection to the NovaTrip SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the saved search history table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_query TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_search(user_query, assistant_response):
    """Save a user's travel request and the generated response."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO saved_searches (
                user_query,
                assistant_response
            )
            VALUES (?, ?)
            """,
            (user_query, assistant_response),
        )


def get_recent_searches(limit=10):
    """Return the most recent saved searches."""
    limit = max(1, min(int(limit), 100))

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, user_query, assistant_response, created_at
            FROM saved_searches
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]