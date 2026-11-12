"""Central configuration for SkyCast.

Settings live in one place so they are easy to find and change.
"""
import os

# The project root folder, used to build the database path.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Settings used when the app runs normally."""

    APP_NAME = "SkyCast"

    # Flask uses this key to sign session data. The fallback is only for local development.
    SECRET_KEY = os.environ.get("SKYCAST_SECRET_KEY", "dev-only-change-me")

    # Maximum seconds to wait for an external weather API.
    REQUEST_TIMEOUT = 10

    # SQLite file that stores recent searches. Created automatically.
    DATABASE_PATH = os.path.join(BASE_DIR, "skycast.db")

    # How many recent searches to keep and show.
    RECENT_SEARCH_LIMIT = 5


class TestingConfig(Config):
    """Settings used by the automated tests."""

    TESTING = True

    # Tests use a separate database file so they never touch real data.
    DATABASE_PATH = os.path.join(BASE_DIR, "test_skycast.db")