"""Automated tests for the Phase 1 foundation.

Run from the project root with: python -m pytest -v
"""

from config import TestingConfig 
from skycast import create_app 


def make_client():
    """Create a Flask test client that uses the testing configuration."""
    app = create_app(TestingConfig)
    return app.test_client()


def test_home_page_loads():
    response = make_client().get("/")
    assert response.status_code == 200
    assert b"SkyCast" in response.data 


def test_health_endpoint_returns_ok():
    response = make_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

def test_unknown_page_returns_404():
    response = make_client().get("/this-page-does-not-exist")
    assert response.status_code == 404