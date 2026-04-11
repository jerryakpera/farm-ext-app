"""
WSGI config for ps119 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

# python_packages
import os

# django_packages
from django.core.wsgi import get_wsgi_application

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


application = get_wsgi_application()
