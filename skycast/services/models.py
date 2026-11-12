"""Simple data containers used by the service layer.

A dataclass automatically creates __init__, __repr__ and __eq__ methods,
so we only describe the fields.
"""
from dataclasses import dataclass


@dataclass
class City:
    """A place returned by the geocoding API."""
    name: str
    country: str
    latitude: float
    longitude: float
    admin1: str = ""  # State or region, for example "Delhi"


@dataclass
class CurrentWeather:
    """Raw current conditions, in the units requested from Open-Meteo."""
    temperature: float
    apparent_temperature: float
    humidity: int
    wind_speed: float
    pressure: float
    weather_code: int
    is_day: bool
    time: str


@dataclass
class HourlyPoint:
    """One hour in the hourly forecast."""
    time: str
    temperature: float
    precipitation_probability: int
    weather_code: int
    humidity: int = 0
    wind_speed: float = 0.0


@dataclass
class DailyPoint:
    """One day in the daily forecast."""
    date: str
    temp_max: float
    temp_min: float
    precipitation_probability: int
    weather_code: int
    sunrise: str
    sunset: str


@dataclass
class Forecast:
    """Everything the forecast API returned for one location."""
    timezone: str
    current: CurrentWeather
    hourly: list
    daily: list