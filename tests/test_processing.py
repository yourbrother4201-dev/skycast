"""Tests for the processing layer.

These tests use no network and no Flask app, because the processing
functions are pure: same input, same output.

Run with:  python -m pytest -v
"""
from skycast.processing.units import (
    celsius_to_fahrenheit,
    format_temperature,
    format_wind,
    kmh_to_mph,
)
from skycast.processing.view_models import (
    build_dashboard_view,
    format_day_label,
    format_hour_label,
)
from skycast.processing.weather_codes import describe_weather_code
from skycast.services.models import (
    CurrentWeather,
    DailyPoint,
    Forecast,
    HourlyPoint,
)


def test_celsius_to_fahrenheit():
    assert celsius_to_fahrenheit(0) == 32
    assert celsius_to_fahrenheit(100) == 212


def test_kmh_to_mph():
    assert round(kmh_to_mph(100), 1) == 62.1


def test_format_temperature_celsius_and_fahrenheit():
    assert format_temperature(22.4) == "22°C"
    assert format_temperature(0, unit="F") == "32°F"


def test_format_wind():
    assert format_wind(10) == "10 km/h"
    assert format_wind(100, unit="mph") == "62 mph"


def test_known_weather_code_day_and_night():
    assert describe_weather_code(0, is_day=True) == ("Clear sky", "sun")
    assert describe_weather_code(0, is_day=False) == ("Clear sky", "moon")


def test_unknown_weather_code_does_not_crash():
    label, icon = describe_weather_code(999)
    assert label == "Unknown"
    assert icon == "cloud"


def test_format_hour_label():
    assert format_hour_label("2026-11-11T18:00") == "6 PM"
    assert format_hour_label("2026-11-11T09:00") == "9 AM"


def test_format_day_label():
    assert format_day_label("2026-11-11") == "Wed 11"


def _sample_forecast():
    """Build a small Forecast object by hand, with no API call."""
    current = CurrentWeather(
        temperature=22.5,
        apparent_temperature=21.0,
        humidity=60,
        wind_speed=9.5,
        pressure=1012.3,
        weather_code=2,
        is_day=False,
        time="2026-11-11T18:00",
    )
    hourly = [HourlyPoint("2026-11-11T18:00", 22.5, 10, 2)]
    daily = [
        DailyPoint(
            date="2026-11-11",
            temp_max=28.0,
            temp_min=14.0,
            precipitation_probability=20,
            weather_code=3,
            sunrise="2026-11-11T06:40",
            sunset="2026-11-11T17:20",
        )
    ]
    return Forecast(timezone="Asia/Kolkata", current=current, hourly=hourly, daily=daily)


def test_dashboard_view_contains_display_values():
    view = build_dashboard_view(_sample_forecast(), unit="C")
    assert view["current"]["temperature"] == "22°C"
    assert view["current"]["condition"] == "Partly cloudy"
    assert view["current"]["icon"] == "cloud-moon"
    assert view["hourly"][0]["time"] == "6 PM"
    assert view["daily"][0]["sunset"] == "17:20"


def test_dashboard_view_fahrenheit():
    view = build_dashboard_view(_sample_forecast(), unit="F")
    assert view["current"]["temperature"] == "72°F"
    assert view["daily"][0]["temp_max"] == "82°F"