"""Build display-ready dictionaries from the forecast objects.

The routes pass these dictionaries to the browser as JSON.
Keeping this logic here means the front end contains almost no calculation.
"""
from datetime import datetime

from skycast.processing.units import format_temperature, format_wind
from skycast.processing.weather_codes import describe_weather_code


def format_hour_label(iso_time):
    """Turn '2026-11-11T18:00' into '6 PM'."""
    dt = datetime.fromisoformat(iso_time)
    return dt.strftime("%I %p").lstrip("0")


def format_day_label(iso_date):
    """Turn '2026-11-11' into 'Wed 11'."""
    dt = datetime.fromisoformat(iso_date)
    return dt.strftime("%a %d")


def format_updated_time(when=None):
    """Return the time of an update, such as '3:45 PM'.

    Passing a datetime makes this easy to test. Without one, the current time is used.
    """
    when = when or datetime.now()
    return when.strftime("%I:%M %p").lstrip("0")


def _convert_temp(celsius, unit):
    """Return the number in the chosen unit, rounded to a whole number."""
    value = celsius if unit == "C" else celsius * 9 / 5 + 32
    return round(value)


def _convert_wind(kmh, unit):
    """Return the wind speed as a whole number. km/h for C, mph for F."""
    return round(kmh) if unit == "C" else round(kmh * 0.621371)


def build_current_view(current, unit="C"):
    """Return the display values for the current-weather card."""
    label, icon = describe_weather_code(current.weather_code, current.is_day)
    return {
        "temperature": format_temperature(current.temperature, unit),
        "feels_like": format_temperature(current.apparent_temperature, unit),
        "humidity": f"{current.humidity}%",
        "wind": format_wind(current.wind_speed, "kmh" if unit == "C" else "mph"),
        "pressure": f"{round(current.pressure)} hPa",
        "condition": label,
        "icon": icon,
        "is_day": current.is_day,
    }


def build_hourly_view(hourly, unit="C"):
    """Return display values for each of the next 24 hours."""
    return [
        {
            "time": format_hour_label(point.time),
            "temperature": _convert_temp(point.temperature, unit),
            "precipitation": f"{point.precipitation_probability}%",
            "icon": describe_weather_code(point.weather_code, True)[1],
            "label": describe_weather_code(point.weather_code, True)[0],
        }
        for point in hourly
    ]


def build_chart_view(hourly, unit="C"):
    """Return parallel lists for the three Chart.js graphs."""
    return {
        "labels": [format_hour_label(p.time) for p in hourly],
        "temperature": [_convert_temp(p.temperature, unit) for p in hourly],
        "humidity": [p.humidity for p in hourly],
        "wind": [_convert_wind(p.wind_speed, unit) for p in hourly],
        "wind_unit": "mph" if unit == "F" else "km/h",
        "temp_unit": "°F" if unit == "F" else "°C",
    }


def build_daily_view(daily, unit="C"):
    """Return display values for each day of the 7-day forecast."""
    return [
        {
            "day": format_day_label(point.date),
            "temp_max": format_temperature(point.temp_max, unit),
            "temp_min": format_temperature(point.temp_min, unit),
            "precipitation": f"{point.precipitation_probability}%",
            "icon": describe_weather_code(point.weather_code, True)[1],
            "label": describe_weather_code(point.weather_code, True)[0],
            "sunrise": point.sunrise[-5:],
            "sunset": point.sunset[-5:],
        }
        for point in daily
    ]


def build_dashboard_view(forecast_data, unit="C"):
    """Combine current, hourly, chart and daily views into one dictionary."""
    return {
        "timezone": forecast_data.timezone,
        "unit": unit,
        "updated_at": format_updated_time(),
        "current": build_current_view(forecast_data.current, unit),
        "hourly": build_hourly_view(forecast_data.hourly, unit),
        "chart": build_chart_view(forecast_data.hourly, unit),
        "daily": build_daily_view(forecast_data.daily, unit),
    }