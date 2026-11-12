# SkyCast

SkyCast is a professional-style weather forecast web application built with
Python (Flask), the free Open-Meteo APIs, HTML, CSS, JavaScript and Chart.js.
No API key is needed.

## Features

- Current weather: temperature, feels-like, humidity, wind, pressure, condition icon.
- Search any city worldwide, with suggestions.
- Browser geolocation with permission handling.
- Next 24 hours and a 7-day forecast.
- Temperature, humidity and wind charts.
- Celsius and Fahrenheit toggle.
- Recent searches stored in SQLite.
- Loading states, friendly error messages and input validation.

## Setup (Windows PowerShell)

    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python run.py

Then open http://127.0.0.1:5000 in your browser.

## Running tests

    python -m pytest -v

Tests never use the internet. External APIs are replaced with fake data.

## Project structure

- `skycast/services/` - talks to Open-Meteo (geocoding, forecast, shared HTTP helper).
- `skycast/processing/` - converts raw data into display values (units, weather codes).
- `skycast/db/` - SQLite recent-searches storage.
- `skycast/routes.py` - page and JSON API routes.
- `skycast/static/js/` - browser code: search, dashboard, charts.
- `tests/` - automated tests for each layer.

## Project status

- Phase 1: Foundation - complete
- Phase 2: Weather and geocoding services - complete
- Phase 3: Data processing - complete
- Phase 4: City search, geolocation and recent searches - complete
- Phase 5: Dashboard UI - complete
- Phase 6: Analytics charts - complete
- Phase 7: Polish and testing - complete