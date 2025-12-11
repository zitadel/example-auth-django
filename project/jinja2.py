from typing import Any

from django.urls import reverse
from jinja2 import Environment


def environment(**options: Any) -> Environment:
    """Configure Jinja2 environment with Django URL resolver."""
    env = Environment(autoescape=True, **options)
    env.globals.update(
        {
            "url_for": lambda route_name, **kwargs: reverse(route_name, kwargs=kwargs),
        }
    )
    return env
