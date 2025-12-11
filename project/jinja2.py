"""Jinja2 environment configuration for Django templates."""

from __future__ import annotations

from django.urls import reverse
from jinja2 import Environment


def environment(**options: dict[str, any]) -> Environment:
    """Configure Jinja2 environment with Django URL resolver."""
    env = Environment(**options)
    env.globals.update(
        {
            "url_for": lambda viewname, **kwargs: reverse(viewname, kwargs=kwargs),
        }
    )
    return env
