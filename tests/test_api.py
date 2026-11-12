"""Tests for the JSON API routes.

The weather and geocoding services are replaced with fake functions, so
these tests never call the internet.
"""
import pytest

from config import TestingConfig
from skycast import create_app
from skycast.services.exceptions import CityNotFoundError
from skycast.services.models import City
from skycast.services import geocoding


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A test client with a temporary database and fake city search."""
    class TempConfig(TestingConfig):
        DATABASE_PATH = str(tmp_path / "api_test.db")

    app = create_app(TempConfig)

    def fake_search(name, count=5):
        if name.lower() == "xyzzyqq":
            raise CityNotFoundError("No city found.")
        return [City("Delhi", "India", 28.65, 77.23, "Delhi")]

    monkeypatch.setattr("skycast.routes.search_cities", fake_search)
    return app.test_client()


def test_search_returns_results(client):
    response = client.get("/api/search?q=Delhi")
    data = response.get_json()
    assert response.status_code == 200
    assert data["results"][0]["name"] == "Delhi"


def test_search_no_match_returns_empty_list(client):
    response = client.get("/api/search?q=xyzzyqq")
    data = response.get_json()
    assert response.status_code == 200
    assert data["results"] == []
    assert "No city" in data["message"]


def test_weather_rejects_missing_coordinates(client):
    response = client.get("/api/weather")
    assert response.status_code == 400


def test_weather_rejects_bad_unit(client):
    response = client.get("/api/weather?lat=1&lon=1&unit=K")
    assert response.status_code == 400


def test_recent_returns_list(client):
    response = client.get("/api/recent")
    assert response.status_code == 200
    assert response.get_json()["results"] == []