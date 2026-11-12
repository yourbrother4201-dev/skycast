"""Tests for the service layer.

The real internet is never used. requests.get is replaced with a fake
function that returns prepared JSON.

Run with:  python -m pytest -v
"""
import pytest
import requests

from config import TestingConfig
from skycast import create_app
from skycast.services import forecast, geocoding
from skycast.services.exceptions import (
    ApiConnectionError,
    ApiResponseError,
    CityNotFoundError,
)


class FakeResponse:
    """Imitates the parts of requests.Response that our code uses."""

    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data


@pytest.fixture
def app():
    """Services read config through current_app, so an app context is needed."""
    app = create_app(TestingConfig)
    with app.app_context():
        yield app


GEOCODE_SAMPLE = {
    "results": [
        {
            "name": "Delhi",
            "country": "India",
            "latitude": 28.6519,
            "longitude": 77.2315,
            "admin1": "Delhi",
        }
    ]
}

FORECAST_SAMPLE = {
    "timezone": "Asia/Kolkata",
    "current": {
        "time": "2026-11-11T18:00",
        "temperature_2m": 22.5,
        "relative_humidity_2m": 60,
        "apparent_temperature": 21.0,
        "is_day": 0,
        "weather_code": 1,
        "surface_pressure": 1012.3,
        "wind_speed_10m": 9.5,
    },
    "hourly": {
        "time": ["2026-11-11T18:00", "2026-11-11T19:00"],
        "temperature_2m": [22.5, 21.8],
        "precipitation_probability": [10, None],
        "weather_code": [1, 2],
        "relative_humidity_2m": [60, 62],
        "wind_speed_10m": [9.5, None],
    },
    "daily": {
        "time": ["2026-11-11"],
        "weather_code": [3],
        "temperature_2m_max": [28.0],
        "temperature_2m_min": [14.0],
        "precipitation_probability_max": [20],
        "sunrise": ["2026-11-11T06:40"],
        "sunset": ["2026-11-11T17:20"],
    },
}


def test_search_cities_returns_city(monkeypatch, app):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(GEOCODE_SAMPLE))
    cities = geocoding.search_cities("Delhi")
    assert cities[0].name == "Delhi"
    assert cities[0].country == "India"


def test_search_cities_no_match_raises(monkeypatch, app):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse({}))
    with pytest.raises(CityNotFoundError):
        geocoding.search_cities("Xyzzyqq")


def test_search_cities_short_query_rejected(app):
    with pytest.raises(CityNotFoundError):
        geocoding.search_cities("a")


def test_connection_error_is_wrapped(monkeypatch, app):
    def broken(*args, **kwargs):
        raise requests.ConnectionError("no internet")

    monkeypatch.setattr(requests, "get", broken)
    with pytest.raises(ApiConnectionError):
        geocoding.search_cities("Delhi")


def test_bad_status_code_raises(monkeypatch, app):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse({}, status_code=500))
    with pytest.raises(ApiResponseError):
        geocoding.search_cities("Delhi")


def test_get_forecast_parses_data(monkeypatch, app):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(FORECAST_SAMPLE))
    result = forecast.get_forecast(28.65, 77.23)
    assert result.timezone == "Asia/Kolkata"
    assert result.current.temperature == 22.5
    assert result.current.is_day is False
    assert len(result.hourly) == 2
    assert result.hourly[1].precipitation_probability == 0  # None became 0
    assert result.hourly[0].humidity == 60
    assert result.hourly[1].wind_speed == 0.0  # None became 0.0
    assert result.daily[0].temp_max == 28.0


def test_get_forecast_incomplete_data_raises(monkeypatch, app):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse({"timezone": "UTC"}))
    with pytest.raises(ApiResponseError):
        forecast.get_forecast(0, 0)