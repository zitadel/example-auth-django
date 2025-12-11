"""Root URL patterns."""

from __future__ import annotations

from django.urls import path

from app import views

urlpatterns = [
    path("", views.home, name="home"),
    path("profile", views.profile, name="profile"),
]
