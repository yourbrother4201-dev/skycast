"""City search using the Open-Meteo Geocoding API.

Docs: https://open-meteo.com/en/docs/geocoding-api
"""
import requests
from flask import current_app

from skycast.services.exceptions import (
    ApiConnectionError,
    ApiResponseError,
    CityNotFoundError,
)
from skycast.services.models import City

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def search_cities(name, count=5):
    """Return a list of City objects that match the name.

    Raises:
        CityNotFoundError: no city matched.
        ApiConnectionError: the API could not be reached.
        ApiResponseError: the API returned an error or unexpected data.
    """
    name = (name or "").strip()
    if len(name) < 2:
        raise CityNotFoundError("Please type at least 2 characters.")

    params = {"name": name, "count": count, "language": "en", "format": "json"}
    data = _get_json(GEOCODING_URL, params)

    # When nothing matches, Open-Meteo leaves out the "results" key entirely.
    results = data.get("results")
    if not results:
        raise CityNotFoundError(f"No city found for '{name}'.")

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


def _get_json(url, params):
    """Send a GET request and return the parsed JSON.

    This helper is shared by the geocoding and forecast modules through
    the import below.
    """
    timeout = current_app.config.get("REQUEST_TIMEOUT", 10)
    try:
        response = requests.get(url, params=params, timeout=timeout)
    except requests.RequestException as exc:
        raise ApiConnectionError("Could not reach the weather service. Check your internet connection.") from exc

    if response.status_code != 200:
        raise ApiResponseError(f"Weather service returned status {response.status_code}.")

    try:
        return response.json()
    except ValueError as exc:
        raise ApiResponseError("Weather service sent data that could not be read.") from exc