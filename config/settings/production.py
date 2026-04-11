"""
Docstring for config.settings.production.
"""

# third_party_packages
from decouple import config

# app_packages
from .base import *
from .base import REST_FRAMEWORK


API_URL = config("API_BASE_URL")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": "localhost",
    }
}

EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]
