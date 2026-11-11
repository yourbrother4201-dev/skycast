"""Unit conversion helpers.

Open-Meteo returns metric values. These functions convert them for display.
"""


def celsius_to_fahrenheit(celsius):
    """Convert degrees Celsius to degrees Fahrenheit."""
    return celsius * 9 / 5 + 32


def kmh_to_mph(kmh):
    """Convert kilometres per hour to miles per hour."""
    return kmh * 0.621371


def format_temperature(celsius, unit="C"):
    """Return a rounded temperature string, such as '22°C' or '72°F'."""
    if unit == "F":
        return f"{round(celsius_to_fahrenheit(celsius))}°F"
    return f"{round(celsius)}°C"


def format_wind(kmh, unit="kmh"):
    """Return a rounded wind speed string, such as '10 km/h' or '6 mph'."""
    if unit == "mph":
        return f"{round(kmh_to_mph(kmh))} mph"
    return f"{round(kmh)} km/h"