"""Custom exceptions for the weather service layer.

Having one base exception lets the web routes catch any weather-service
problem in a single place, without knowing which API failed.
"""


class WeatherServiceError(Exception):
    """Base class for all errors raised by the service layer."""


class ApiConnectionError(WeatherServiceError):
    """The API could not be reached (no internet, timeout, DNS problem)."""


class ApiResponseError(WeatherServiceError):
    """The API replied, but with an error status or unexpected data."""


class CityNotFoundError(WeatherServiceError):
    """The geocoding API found no city matching the search text."""