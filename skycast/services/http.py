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
    except requests.Timeout as exc:
        raise ApiConnectionError(
            "The weather service took too long to respond. Please try again."
        ) from exc
    except requests.RequestException as exc:
        raise ApiConnectionError(
            "Could not reach the weather service. Your internet connection may be down."
        ) from exc

    if response.status_code != 200:
        raise ApiResponseError(
            f"The weather service returned an error (status {response.status_code}). Please try again later."
        )

    try:
        return response.json()
    except ValueError as exc:
        raise ApiResponseError("The weather service sent data that could not be read.") from exc