"""Authentication URL patterns."""

from __future__ import annotations

from django.urls import path

from lib import auth

urlpatterns = [
    path("csrf", auth.csrf, name="csrf"),
    path("signin", auth.signin, name="signin"),
    path("signin/zitadel", auth.signin_zitadel, name="signin_zitadel"),
    path("callback", auth.callback, name="callback"),
    path("logout", auth.logout, name="logout"),
    path("logout/callback", auth.logout_callback, name="logout_callback"),
    path("logout/success", auth.logout_success, name="logout_success"),
    path("logout/error", auth.logout_error, name="logout_error"),
    path("error", auth.error_page, name="error"),
    path("userinfo", auth.userinfo, name="userinfo"),
]
