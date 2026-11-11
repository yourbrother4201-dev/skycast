"""Web routes for SkyCast.

A blueprint groups related routes. Later phases add API routes to this
project in the same way.
"""

from flask import Blueprint, current_app, render_template 
main_bp  = Blueprint("main",__name__)


@main_bp.route("/")
def index():
    """Show the home page."""
    return render_template("index.html",app_name=current_app.config["APP_NAME"])


@main_bp.route("/health")
def health():
    """Return a small JSON response that proves the server is alive.
    Flask converts the Python dictionary into JSON automatically.
    """
    return {"status":"ok","app":current_app.config["APP_NAME"]}

