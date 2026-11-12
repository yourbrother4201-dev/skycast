"""Weather forecast using the Open-Meteo Forecast API.

Docs: https://open-meteo.com/en/docs
"""
from skycast.services.exceptions import ApiResponseError
from skycast.services.http import get_json
from skycast.services.models import CurrentWeather, DailyPoint, Forecast, HourlyPoint

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

CURRENT_VARIABLES = (
    "temperature_2m,relative_humidity_2m,apparent_temperature,"
    "is_day,weather_code,surface_pressure,wind_speed_10m"
)
HOURLY_VARIABLES = (
    "temperature_2m,precipitation_probability,weather_code,"
    "relative_humidity_2m,wind_speed_10m"
)
DAILY_VARIABLES = (
    "weather_code,temperature_2m_max,temperature_2m_min,"
    "precipitation_probability_max,sunrise,sunset"
)


def get_forecast(latitude, longitude):
    """Fetch current, hourly and daily weather for a coordinate.

    Units are metric (Celsius, km/h, hPa). The processing layer converts units.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": CURRENT_VARIABLES,
        "hourly": HOURLY_VARIABLES,
        "daily": DAILY_VARIABLES,
        "forecast_days": 7,
        "timezone": "auto",
        "wind_speed_unit": "kmh",
    }
    data = get_json(FORECAST_URL, params)

    try:
        return Forecast(
            timezone=data["timezone"],
            current=_parse_current(data["current"]),
            hourly=_parse_hourly(data["hourly"]),
            daily=_parse_daily(data["daily"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ApiResponseError("Weather data was incomplete.") from exc


def _parse_current(raw):
    """Turn the 'current' block into a CurrentWeather object."""
    return CurrentWeather(
        temperature=float(raw["temperature_2m"]),
        apparent_temperature=float(raw["apparent_temperature"]),
        humidity=int(raw["relative_humidity_2m"]),
        wind_speed=float(raw["wind_speed_10m"]),
        pressure=float(raw["surface_pressure"]),
        weather_code=int(raw["weather_code"]),
        is_day=bool(raw["is_day"]),
        time=raw["time"],
    )


def _parse_hourly(raw):
    """Turn the parallel 'hourly' lists into HourlyPoint objects.

    The first 24 entries are the next 24 hours.
    """
    rows = zip(
        raw["time"],
        raw["temperature_2m"],
        raw["precipitation_probability"],
        raw["weather_code"],
        raw["relative_humidity_2m"],
        raw["wind_speed_10m"],
    )
    points = []
    for time, temp, precip, code, humidity, wind in list(rows)[:24]:
        points.append(
            HourlyPoint(
                time=time,
                temperature=float(temp),
                precipitation_probability=int(precip or 0),
                weather_code=int(code),
                humidity=int(humidity or 0),
                wind_speed=float(wind or 0.0),
            )
        )
    return points


def _parse_daily(raw):
    """Turn the parallel 'daily' lists into DailyPoint objects."""
    rows = zip(
        raw["time"],
        raw["temperature_2m_max"],
        raw["temperature_2m_min"],
        raw["precipitation_probability_max"],
        raw["weather_code"],
        raw["sunrise"],
        raw["sunset"],
    )
    points = []
    for date, tmax, tmin, precip, code, sunrise, sunset in rows:
        points.append(
            DailyPoint(
                date=date,
                temp_max=float(tmax),
                temp_min=float(tmin),
                precipitation_probability=int(precip or 0),
                weather_code=int(code),
                sunrise=sunrise,
                sunset=sunset,
            )
        )
    return points