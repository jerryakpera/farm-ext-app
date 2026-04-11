"""
Docstring for config.settings.local.
"""

# third_party_packages
from decouple import config

# app_packages
from .base import *


API_URL = "http://localhost:8000/api"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": "localhost",
    }
}

SITE_DOMAIN = "http://localhost:8000"
SITE_ID = 2

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
