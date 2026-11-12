"""Tests for the recent-searches database layer.

Each test gets its own temporary database file, so tests never interfere
with each other or with the real skycast.db.
"""
import pytest

from skycast.db.recent_searches import get_recent_searches, init_db, save_search


@pytest.fixture
def db_path(tmp_path):
    """Create a fresh database file inside pytest's temporary folder."""
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


def test_save_and_read_recent_search(db_path):
    save_search(db_path, "Delhi", "India", 28.65, 77.23)
    rows = get_recent_searches(db_path)
    assert len(rows) == 1
    assert rows[0]["name"] == "Delhi"


def test_duplicate_cities_are_shown_once(db_path):
    save_search(db_path, "Delhi", "India", 28.65, 77.23)
    save_search(db_path, "Delhi", "India", 28.65, 77.23)
    assert len(get_recent_searches(db_path)) == 1


def test_limit_is_respected(db_path):
    for i in range(10):
        save_search(db_path, f"City{i}", "Test", float(i), float(i))
    assert len(get_recent_searches(db_path, limit=3)) == 3


def test_empty_database_returns_empty_list(db_path):
    assert get_recent_searches(db_path) == []