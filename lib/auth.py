"""ZITADEL authentication routes using Authlib Django integration."""

from __future__ import annotations

import logging
import secrets
from typing import Any, cast
from urllib.parse import urlencode

from authlib.integrations.django_client import OAuth
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from lib.config import config
from lib.guard import require_auth
from lib.message import get_message
from lib.scopes import ZITADEL_SCOPES

logger = logging.getLogger(__name__)

oauth = OAuth()


def get_well_known_url(domain: str) -> str:
    return f"{domain}/.well-known/openid-configuration"


def init_oauth() -> None:
    """Initialize OAuth client with Django configuration."""
    oauth.register(
        name="zitadel",
        client_id=config.ZITADEL_CLIENT_ID,
        client_secret=config.ZITADEL_CLIENT_SECRET,
        server_metadata_url=get_well_known_url(config.ZITADEL_DOMAIN),
        client_kwargs={
            "scope": ZITADEL_SCOPES,
            "code_challenge_method": "S256",
        },
    )


init_oauth()


@require_GET
def csrf(request: HttpRequest) -> JsonResponse:
    """Generate CSRF token for form submissions."""
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_urlsafe(32)
    return JsonResponse({"csrfToken": request.session["csrf_token"]})


@require_GET
def signin(request: HttpRequest) -> HttpResponse:
    """Render the sign-in page."""
    error = request.GET.get("error")
    providers = [
        {
            "id": "zitadel",
            "name": "ZITADEL",
            "signinUrl": "/auth/signin/zitadel",
        }
    ]
    return render(
        request,
        "auth/signin.html",
        {
            "providers": providers,
            "callbackUrl": request.GET.get("callbackUrl") or config.ZITADEL_POST_LOGIN_URL,
            "message": get_message(error, "signin-error") if error else None,
        },
    )


@require_POST
def signin_zitadel(request: HttpRequest) -> HttpResponse:
    """Initiate OAuth 2.0 authorization flow with PKCE."""
    csrf_token = request.POST.get("csrfToken")
    stored_token = request.session.get("csrf_token")

    if not csrf_token or not stored_token or not secrets.compare_digest(csrf_token, stored_token):
        logger.warning("CSRF token validation failed")
        return redirect("/auth/signin?error=verification")

    request.session.pop("csrf_token", None)
    request.session["post_login_url"] = request.POST.get("callbackUrl", config.ZITADEL_POST_LOGIN_URL)

    redirect_uri = config.ZITADEL_CALLBACK_URL
    logger.info("Initiating OAuth authorization flow")
    return cast(HttpResponse, oauth.zitadel.authorize_redirect(request, redirect_uri))


@require_GET
def callback(request: HttpRequest) -> HttpResponse:
    """Handle OAuth 2.0 callback from ZITADEL."""
    try:
        token = oauth.zitadel.authorize_access_token(request)

        userinfo = oauth.zitadel.userinfo(token=token)  # Add token parameter

        old_session_data = dict(request.session)
        request.session.clear()
        for key, value in old_session_data.items():
            if key in ("post_login_url",):
                request.session[key] = value

        request.session["auth_session"] = {
            "user": userinfo,
            "access_token": token.get("access_token"),
            "id_token": token.get("id_token"),
            "refresh_token": token.get("refresh_token"),
            "expires_at": token.get("expires_at"),
        }

        post_login_url = request.session.pop("post_login_url", config.ZITADEL_POST_LOGIN_URL)
        logger.info(f"Authentication successful for user: {userinfo.get('sub')}")
        return redirect(post_login_url)

    except Exception as e:
        logger.exception("Token exchange failed: %s", str(e))
        return redirect("/auth/error?error=callback")


@require_POST
def logout(request: HttpRequest) -> HttpResponse:
    """Initiate logout flow with ZITADEL."""
    try:
        logout_state = secrets.token_urlsafe(32)
        request.session["logout_state"] = logout_state

        metadata = oauth.zitadel.load_server_metadata()
        end_session_endpoint = metadata.get("end_session_endpoint")

        if end_session_endpoint:
            params = {
                "post_logout_redirect_uri": config.ZITADEL_POST_LOGOUT_URL,
                "client_id": config.ZITADEL_CLIENT_ID,
                "state": logout_state,
            }
            logout_url = f"{end_session_endpoint}?{urlencode(params)}"
            logger.info("Initiating logout flow")
            return redirect(logout_url)

        request.session.clear()
        return redirect(config.ZITADEL_POST_LOGOUT_URL)

    except Exception as e:
        logger.exception("Logout initiation failed: %s", str(e))
        request.session.clear()
        return redirect(config.ZITADEL_POST_LOGOUT_URL)


@require_GET
def logout_callback(request: HttpRequest) -> HttpResponse:
    """Handle logout callback from ZITADEL with state validation."""
    received_state = request.GET.get("state")
    stored_state = request.session.get("logout_state")

    if received_state and stored_state and secrets.compare_digest(received_state, stored_state):
        request.session.clear()
        logger.info("Logout successful")
        return redirect("/auth/logout/success")

    logger.warning("Logout state validation failed")
    reason = "Invalid or missing state parameter."
    return redirect(f"/auth/logout/error?reason={reason}")


@require_GET
def logout_success(request: HttpRequest) -> HttpResponse:
    """Display logout success page."""
    return render(request, "auth/logout/success.html")


@require_GET
def logout_error(request: HttpRequest) -> HttpResponse:
    """Display logout error page."""
    reason = request.GET.get("reason", "An unknown error occurred.")
    return render(request, "auth/logout/error.html", {"reason": reason})


@require_GET
def error_page(request: HttpRequest) -> HttpResponse:
    """Display authentication error page."""
    error_code = request.GET.get("error")
    msg = get_message(error_code, "auth-error")
    return render(request, "auth/error.html", msg)


@require_GET
@require_auth
def userinfo(request: HttpRequest) -> JsonResponse:
    """Fetch fresh user information from ZITADEL."""
    auth_session = request.session.get("auth_session", {})
    access_token = auth_session.get("access_token")

    if not access_token:
        logger.warning("Userinfo request without access token")
        return JsonResponse({"error": "No access token available"}, status=401)

    try:
        metadata = oauth.zitadel.load_server_metadata()
        userinfo_endpoint = metadata.get("userinfo_endpoint")

        headers = {"Authorization": f"Bearer {access_token}"}
        response = oauth.zitadel._client.get(userinfo_endpoint, headers=headers)
        response.raise_for_status()

        logger.info("Userinfo fetched successfully")
        result: dict[str, Any] = response.json()
        return JsonResponse(result)

    except Exception as e:
        logger.exception("Userinfo fetch failed: %s", str(e))
        return JsonResponse({"error": "Failed to fetch user info"}, status=500)
