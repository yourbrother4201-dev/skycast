"""Map WMO weather codes to a human-readable label and an icon name.

WMO codes are an international standard. Open-Meteo uses them in its
weather_code field. Full list: https://open-meteo.com/en/docs (WMO Weather interpretation codes)

Icon names refer to files or CSS classes that the front end will use in Phase 5.
"""

# Each code maps to (label, icon_day, icon_night).
WEATHER_CODES = {
    0: ("Clear sky", "sun", "moon"),
    1: ("Mainly clear", "sun", "moon"),
    2: ("Partly cloudy", "cloud-sun", "cloud-moon"),
    3: ("Overcast", "cloud", "cloud"),
    45: ("Fog", "fog", "fog"),
    48: ("Depositing rime fog", "fog", "fog"),
    51: ("Light drizzle", "drizzle", "drizzle"),
    53: ("Moderate drizzle", "drizzle", "drizzle"),
    55: ("Dense drizzle", "drizzle", "drizzle"),
    56: ("Light freezing drizzle", "drizzle", "drizzle"),
    57: ("Dense freezing drizzle", "drizzle", "drizzle"),
    61: ("Slight rain", "rain", "rain"),
    63: ("Moderate rain", "rain", "rain"),
    65: ("Heavy rain", "rain", "rain"),
    66: ("Light freezing rain", "rain", "rain"),
    67: ("Heavy freezing rain", "rain", "rain"),
    71: ("Slight snow", "snow", "snow"),
    73: ("Moderate snow", "snow", "snow"),
    75: ("Heavy snow", "snow", "snow"),
    77: ("Snow grains", "snow", "snow"),
    80: ("Slight rain showers", "rain", "rain"),
    81: ("Moderate rain showers", "rain", "rain"),
    82: ("Violent rain showers", "rain", "rain"),
    85: ("Slight snow showers", "snow", "snow"),
    86: ("Heavy snow showers", "snow", "snow"),
    95: ("Thunderstorm", "storm", "storm"),
    96: ("Thunderstorm with hail", "storm", "storm"),
    99: ("Thunderstorm with heavy hail", "storm", "storm"),
}

UNKNOWN_CODE = ("Unknown", "cloud", "cloud")


def describe_weather_code(code, is_day=True):
    """Return (label, icon) for a WMO code.

    Unknown codes fall back to a neutral label instead of crashing.
    """
    label, icon_day, icon_night = WEATHER_CODES.get(code, UNKNOWN_CODE)
    icon = icon_day if is_day else icon_night
    return label, icon