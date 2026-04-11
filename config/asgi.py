"""
ASGI config for ps119 project.
"""

# python_packages
import os

# django_packages
from django.core.asgi import get_asgi_application

# app_packages
from .settings import base


if base.DEBUG:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "config.settings.local",
    )
else:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "config.settings.production",
    )

application = get_asgi_application()
