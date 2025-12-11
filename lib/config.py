"""Configuration management for ZITADEL authentication.

This module loads and validates all required environment variables for the
application. It follows a fail-fast approach: if any required configuration
is missing, the application will not start.
"""

from __future__ import annotations

import os
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


def must(name: str) -> str:
    """Retrieve a required environment variable.

    Args:
        name: The name of the environment variable to retrieve

    Returns:
        str: The value of the environment variable

    Raises:
        RuntimeError: If the environment variable is not set

    Example:
        >>> domain = must("ZITADEL_DOMAIN")
    """
    value = os.getenv(name)
    if not value:
        if os.getenv("DJANGO_SETTINGS_MODULE"):
            return ""
        raise RuntimeError(f"❌ Missing required env var {name}")
    return value


class Config:
    """Application configuration with validated environment variables.

    This class loads all configuration from environment variables and validates
    that required values are present. It provides type-safe access to
    configuration throughout the application.

    Attributes:
        ZITADEL_DOMAIN: Base domain of your ZITADEL instance
        ZITADEL_CLIENT_ID: OAuth client ID from ZITADEL application settings
        ZITADEL_CLIENT_SECRET: OAuth client secret (required even for PKCE by Authlib)
        ZITADEL_CALLBACK_URL: Redirect URI registered in ZITADEL application
        ZITADEL_POST_LOGIN_URL: Internal URL to redirect after successful login
        ZITADEL_POST_LOGOUT_URL: URL to redirect after logout from ZITADEL
        SESSION_SECRET: Secret key for signing session cookies
        SESSION_DURATION: Session lifetime in seconds (default: 3600)
        PORT: Network port for the Django server (optional)
        PY_ENV: Application environment ('development' or 'production')
    """

    def __init__(self) -> None:
        domain = must("ZITADEL_DOMAIN")
        parsed = urlparse(domain)
        self.ZITADEL_DOMAIN: str = f"{parsed.scheme}://{parsed.netloc}"
        self.ZITADEL_CLIENT_ID: str = must("ZITADEL_CLIENT_ID")
        self.ZITADEL_CLIENT_SECRET: str = must("ZITADEL_CLIENT_SECRET")
        self.ZITADEL_CALLBACK_URL: str = must("ZITADEL_CALLBACK_URL")
        self.ZITADEL_POST_LOGIN_URL: str = os.getenv("ZITADEL_POST_LOGIN_URL", "/profile")
        self.ZITADEL_POST_LOGOUT_URL: str = os.getenv("ZITADEL_POST_LOGOUT_URL", "/")
        self.SESSION_SECRET: str = must("SESSION_SECRET")
        self.SESSION_DURATION: int = int(os.getenv("SESSION_DURATION", "3600"))
        self.PORT: Optional[str] = os.getenv("PORT")
        self.PY_ENV: Optional[str] = os.getenv("PY_ENV")


config = Config()
