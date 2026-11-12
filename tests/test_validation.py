"""Tests for input validation and small helper functions.

No network is used. The validation runs before any API call.
"""
from datetime import datetime

import pytest

from skycast.processing.view_models import format_updated_time
from skycast.services.exceptions import CityNotFoundError
from skycast.services.geocoding import MAX_QUERY_LENGTH, validate_city_query


def test_valid_city_name_is_returned_trimmed():
    assert validate_city_query("  New York  ") == "New York"


def test_accented_letters_are_allowed():
    assert validate_city_query("São Paulo") == "São Paulo"


def test_too_short_is_rejected():
    with pytest.raises(CityNotFoundError):
        validate_city_query("a")


def test_too_long_is_rejected():
    with pytest.raises(CityNotFoundError, match="100 characters"):
        validate_city_query("a" * (MAX_QUERY_LENGTH + 1))


@pytest.mark.parametrize("bad", ["<script>", "Delhi;DROP", "123abc", "Del$hi"])
def test_unusual_characters_are_rejected(bad):
    with pytest.raises(CityNotFoundError):
        validate_city_query(bad)


def test_format_updated_time_removes_leading_zero():
    assert format_updated_time(datetime(2026, 11, 12, 9, 5)) == "9:05 AM"
    assert format_updated_time(datetime(2026, 11, 12, 15, 45)) == "3:45 PM"