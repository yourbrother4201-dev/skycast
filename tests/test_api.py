"""Tests for the JSON API routes.

Geocoding and forecast calls are replaced with fake functions, so these
tests never use the internet.
"""
import pytest

from config import TestingConfig
from skycast import create_app
from skycast.services.exceptions import CityNotFoundError
from skycast.services.models import City, CurrentWeather, DailyPoint, Forecast, HourlyPoint


def _fake_forecast():
    """A small Forecast object built by hand."""
    return Forecast(
        timezone="Asia/Kolkata",
        current=CurrentWeather(
            temperature=22.0,
            apparent_temperature=21.0,
            humidity=60,
            wind_speed=9.5,
            pressure=1012.3,
            weather_code=2,
            is_day=False,
            time="2026-11-11T18:00",
        ),
        hourly=[HourlyPoint("2026-11-11T18:00", 22.0, 10, 2)],
        daily=[
            DailyPoint(
                date="2026-11-11",
                temp_max=28.0,
                temp_min=14.0,
                precipitation_probability=20,
                weather_code=3,
                sunrise="2026-11-11T06:40",
                sunset="2026-11-11T17:20",
            )
        ],
    )


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A test client with a temporary database and fake services."""
    class TempConfig(TestingConfig):
        DATABASE_PATH = str(tmp_path / "api_test.db")

    app = create_app(TempConfig)

    def fake_search(name, count=5):
        if name.lower() == "xyzzyqq":
            raise CityNotFoundError("No city found.")
        return [City("Delhi", "India", 28.65, 77.23, "Delhi")]

    monkeypatch.setattr("skycast.routes.search_cities", fake_search)
    monkeypatch.setattr("skycast.routes.get_forecast", lambda lat, lon: _fake_forecast())
    return app.test_client()


def test_search_returns_results(client):
    response = client.get("/api/search?q=Delhi")
    assert response.status_code == 200
    assert response.get_json()["results"][0]["name"] == "Delhi"


def test_search_no_match_returns_empty_list(client):
    data = client.get("/api/search?q=xyzzyqq").get_json()
    assert data["results"] == []
    assert "No city" in data["message"]


def test_weather_rejects_missing_coordinates(client):
    assert client.get("/api/weather").status_code == 400


def test_weather_rejects_bad_unit(client):
    assert client.get("/api/weather?lat=1&lon=1&unit=K").status_code == 400


def test_weather_celsius_output(client):
    data = client.get("/api/weather?lat=28.65&lon=77.23&unit=C").get_json()
    assert data["unit"] == "C"
    assert data["current"]["temperature"] == "22°C"


def test_weather_fahrenheit_output(client):
    data = client.get("/api/weather?lat=28.65&lon=77.23&unit=F").get_json()
    assert data["unit"] == "F"
    assert data["current"]["temperature"] == "72°F"


def test_recent_returns_list(client):
    response = client.get("/api/recent")
    assert response.status_code == 200
    assert response.get_json()["results"] == []