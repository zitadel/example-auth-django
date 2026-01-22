"""Authentication URL patterns."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

from django.urls import path

from lib import auth

if TYPE_CHECKING:
    from django.http import HttpResponseBase
    from django.http.request import HttpRequest

    ViewFunc = Callable[[HttpRequest], HttpResponseBase]

urlpatterns = [
    path("csrf", cast("ViewFunc", auth.csrf), name="csrf"),
    path("signin", cast("ViewFunc", auth.signin), name="signin"),
    path("signin/zitadel", cast("ViewFunc", auth.signin_zitadel), name="signin_zitadel"),
    path("callback", cast("ViewFunc", auth.callback), name="callback"),
    path("logout", cast("ViewFunc", auth.logout), name="logout"),
    path("logout/callback", cast("ViewFunc", auth.logout_callback), name="logout_callback"),
    path("logout/success", cast("ViewFunc", auth.logout_success), name="logout_success"),
    path("logout/error", cast("ViewFunc", auth.logout_error), name="logout_error"),
    path("error", cast("ViewFunc", auth.error_page), name="error"),
    path("userinfo", cast("ViewFunc", auth.userinfo), name="userinfo"),
]
