# test/test_app.py
"""Basic smoke tests for application."""

from __future__ import annotations

import pytest
from django.test import Client


@pytest.mark.django_db
def test_home_page_loads() -> None:
    """Test that home page loads and returns 200."""
    client = Client()
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_signin_page_loads() -> None:
    """Test that sign-in page loads."""
    client = Client()
    response = client.get("/auth/signin")
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_redirects_when_unauthenticated() -> None:
    """Test that profile page redirects to sign-in when not authenticated."""
    client = Client()
    response = client.get("/profile", follow=False)
    assert response.status_code == 302


@pytest.mark.django_db
def test_csrf_endpoint_works() -> None:
    """Test that CSRF endpoint returns a token."""
    client = Client()
    response = client.get("/auth/csrf")
    assert response.status_code == 200
