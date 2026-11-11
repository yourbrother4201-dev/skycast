"""SkyCast package.

The create_app() function is an "application factory". It builds and configures
the Flask app. Using a factory lets the tests create a separate app with
different settings.
"""
from flask import Flask

from config import Config


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Import here to avoid circular imports, then register the route group.
    from skycast.routes import main_bp
    app.register_blueprint(main_bp)

    return app