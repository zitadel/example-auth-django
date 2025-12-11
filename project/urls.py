"""URL configuration for ZITADEL authentication project."""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("auth/", include("app.urls.auth")),
    path("", include("app.urls.root")),
]
