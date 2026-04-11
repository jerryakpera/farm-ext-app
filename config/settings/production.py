"""
Docstring for config.settings.production.
"""

from decouple import config

# app_packages
from .base import *

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
