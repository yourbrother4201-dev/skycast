"""City search using the Open-Meteo Geocoding API.

Docs: https://open-meteo.com/en/docs/geocoding-api
"""
import re

from skycast.services.exceptions import CityNotFoundError
from skycast.services.http import get_json
from skycast.services.models import City

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
MAX_QUERY_LENGTH = 100

# Letters (including accented ones), spaces, commas, periods, hyphens and apostrophes.
ALLOWED_QUERY = re.compile(r"^[A-Za-z\u00C0-\u024F][A-Za-z\u00C0-\u024F ,.\-']*$")


def validate_city_query(name):
    """Return a cleaned city name, or raise CityNotFoundError if it is not allowed.

    Validation happens before any network call, so bad input never reaches the API.
    """
    cleaned = (name or "").strip()
    if len(cleaned) < 2:
        raise CityNotFoundError("Please type at least 2 characters.")
    if len(cleaned) > MAX_QUERY_LENGTH:
        raise CityNotFoundError(f"City names must be {MAX_QUERY_LENGTH} characters or fewer.")
    if not ALLOWED_QUERY.match(cleaned):
        raise CityNotFoundError("City names can only contain letters, spaces, commas, periods, hyphens and apostrophes.")
    return cleaned


def search_cities(name, count=5):
    """Return a list of City objects that match the name.

    Raises:
        CityNotFoundError: no city matched, or the search text is not valid.
        ApiConnectionError: the API could not be reached.
        ApiResponseError: the API returned an error or unexpected data.
    """
    cleaned = validate_city_query(name)

    params = {"name": cleaned, "count": count, "language": "en", "format": "json"}
    data = get_json(GEOCODING_URL, params)

    # When nothing matches, Open-Meteo leaves out the "results" key entirely.
    results = data.get("results")
    if not results:
        raise CityNotFoundError(f"No city found for '{cleaned}'. Check the spelling and try again.")

    return [_to_city(item) for item in results]


def _to_city(item):
    """Convert one raw API result into a City object."""
    return City(
        name=item.get("name", "Unknown"),
        country=item.get("country", ""),
        latitude=float(item["latitude"]),
        longitude=float(item["longitude"]),
        admin1=item.get("admin1", ""),
    )