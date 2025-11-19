"""
Backend configuration module
Handles environment-specific settings and validates required API keys
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')

# API Keys
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")

# API endpoints
BASE_URL = "https://serpapi.com/search.json"


def validate_config():
    """
    Validate that required configuration is present
    Raises ValueError if critical configuration is missing in production
    """
    errors = []
    warnings = []

    # Check for required API keys
    if not SERPAPI_KEY:
        msg = "SERPAPI_KEY environment variable is not set"
        if FLASK_ENV == 'production':
            errors.append(msg)
        else:
            warnings.append(msg)

    if not GOOGLE_CLOUD_API_KEY:
        msg = "GOOGLE_CLOUD_API_KEY environment variable is not set"
        if FLASK_ENV == 'production':
            errors.append(msg)
        else:
            warnings.append(msg)

    # Print warnings
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    # Raise errors in production
    if errors:
        error_msg = "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)

    return True


# Optionally validate on import (disabled by default to allow testing)
# Uncomment the line below to validate configuration on module import
# validate_config()
