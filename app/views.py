"""Application views for public and protected pages."""

from __future__ import annotations

import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from lib.guard import require_auth


def home(request: HttpRequest) -> HttpResponse:
    """Render the home page with authentication status."""
    session_data = request.session.get("auth_session")
    return render(
        request,
        "index.html",
        {
            "isAuthenticated": bool(session_data),
            "loginUrl": "/auth/signin/zitadel",
        },
    )


@require_auth
def profile(request: HttpRequest) -> HttpResponse:
    """Display authenticated user's profile information."""
    auth_session = request.session.get("auth_session", {})
    user_json = json.dumps(auth_session.get("user", {}), indent=2)
    return render(request, "profile.html", {"userJson": user_json})
