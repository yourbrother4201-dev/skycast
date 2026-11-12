"""Web routes and JSON API routes for SkyCast.

Page routes return HTML. API routes return JSON for the JavaScript code.
Each API route is a thin layer: it validates input, calls the service and
processing layers, and returns the result.
"""
from flask import Blueprint, current_app, jsonify, render_template, request

from skycast.db.recent_searches import get_recent_searches, save_search
from skycast.processing.view_models import build_dashboard_view
from skycast.services.exceptions import CityNotFoundError, WeatherServiceError
from skycast.services.forecast import get_forecast
from skycast.services.geocoding import search_cities

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Show the home page."""
    return render_template("index.html", app_name=current_app.config["APP_NAME"])


@main_bp.route("/health")
def health():
    """Return a small JSON response that proves the server is alive."""
    return {"status": "ok", "app": current_app.config["APP_NAME"]}


@main_bp.route("/api/search")
def api_search():
    """Return up to 5 cities matching ?q=. Used for search suggestions."""
    query = request.args.get("q", "")
    try:
        cities = search_cities(query, count=5)
    except CityNotFoundError as exc:
        return jsonify({"results": [], "message": str(exc)}), 200
    except WeatherServiceError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify({
        "results": [
            {
                "name": c.name,
                "country": c.country,
                "admin1": c.admin1,
                "latitude": c.latitude,
                "longitude": c.longitude,
            }
            for c in cities
        ]
    })


@main_bp.route("/api/weather")
def api_weather():
    """Return processed dashboard data for ?lat=&lon=&unit=C|F&name=&country=.

    name and country are optional. When name is given, the search is saved.
    """
    try:
        latitude = float(request.args["lat"])
        longitude = float(request.args["lon"])
    except (KeyError, ValueError):
        return jsonify({"error": "Latitude and longitude are required numbers."}), 400

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return jsonify({"error": "Latitude or longitude is out of range."}), 400

    unit = request.args.get("unit", "C").upper()
    if unit not in ("C", "F"):
        return jsonify({"error": "Unit must be C or F."}), 400

    try:
        forecast_data = get_forecast(latitude, longitude)
    except WeatherServiceError as exc:
        return jsonify({"error": str(exc)}), 503

    name = request.args.get("name")
    country = request.args.get("country", "")
    if name:
        save_search(current_app.config["DATABASE_PATH"], name, country, latitude, longitude)

    return jsonify(build_dashboard_view(forecast_data, unit))


@main_bp.route("/api/recent")
def api_recent():
    """Return the most recent searches, newest first."""
    limit = current_app.config["RECENT_SEARCH_LIMIT"]
    rows = get_recent_searches(current_app.config["DATABASE_PATH"], limit)
    return jsonify({"results": rows})