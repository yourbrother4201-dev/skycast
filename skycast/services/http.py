"""Shared HTTP helper for all Open-Meteo requests.

Both the geocoding and forecast modules use this function, so the timeout,
connection handling and error wrapping are written only once.
"""
import requests
from flask import current_app

from skycast.services.exceptions import ApiConnectionError, ApiResponseError


def get_json(url, params):
    """Send a GET request and return the parsed JSON.

    Raises:
        ApiConnectionError: the server could not be reached or timed out.
        ApiResponseError: the server replied with an error or invalid JSON.
    """
    timeout = current_app.config.get("REQUEST_TIMEOUT", 10)
    try:
        response = requests.get(url, params=params, timeout=timeout)
    except requests.RequestException as exc:
        raise ApiConnectionError(
            "Could not reach the weather service. Check your internet connection."
        ) from exc

    if response.status_code != 200:
        raise ApiResponseError(
            f"Weather service returned status {response.status_code}."
        )

    try:
        return response.json()
    except ValueError as exc:
        raise ApiResponseError("Weather service sent data that could not be read.") from exc