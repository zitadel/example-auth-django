from typing import Any

from django.urls import reverse
from jinja2 import Environment


def environment(**options: Any) -> Environment:
    """Configure Jinja2 environment with Django URL resolver."""
    options.setdefault("autoescape", True)
    env = Environment(**options)  # noqa: S701
    env.globals.update(
        {
            "url_for": lambda route_name, **kwargs: reverse(route_name, kwargs=kwargs),
        }
    )
    return env
