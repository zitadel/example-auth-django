from typing import Any

from jinja2 import Environment
from django.urls import reverse


def environment(**options: Any) -> Environment:
    """Configure Jinja2 environment with Django URL resolver."""
    env = Environment(autoescape=True, **options)
    env.globals.update(
        {
            "url_for": lambda route_name, **kwargs: reverse(route_name, kwargs=kwargs),
        }
    )
    return env
