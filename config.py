"""Central configuration for SkyCast.
Settings live in one place so they are easy to find the change."""

import os 

class Config:
    """Settings used when the app runs normally."""

    APP_NAME = "SkyCast"


    #Flask uses this key to sign session data.The fallback is only for local development.
    SECRET_KEY = os.environ.get("SKYCAST_SECRET_KEY","dev-only-change-me")

    #Maximum seconds to wait for an external weather API (used from Phase 2). 
    REQUEST_TIMEOUT = 10

class TestingConfig(Config):
    """Settings used by the automated tests."""

    TESTING = True 


