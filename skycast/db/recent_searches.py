"""Store and read recent city searches in SQLite.

sqlite3 is part of Python's standard library, so no installation is needed.
Every function opens its own connection, which keeps the code simple and
safe for Flask's threaded server.
"""
import sqlite3
from datetime import datetime


def _connect(db_path):
    """Open a connection and return rows that can be read by column name."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path):
    """Create the recent_searches table if it does not exist yet."""
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recent_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                country TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                searched_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_search(db_path, name, country, latitude, longitude):
    """Save a city the user looked at. Returns nothing."""
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO recent_searches (name, country, latitude, longitude, searched_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, country, latitude, longitude, datetime.now().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def get_recent_searches(db_path, limit=5):
    """Return the most recent unique cities, newest first, as plain dictionaries."""
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT name, country, latitude, longitude, MAX(searched_at) AS searched_at
            FROM recent_searches
            GROUP BY name, country, latitude, longitude
            ORDER BY searched_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()