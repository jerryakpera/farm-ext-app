"""
Docstring for config.settings.production.
"""

# third_party_packages
from decouple import config

# app_packages
from .base import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("MYSQL_DB"),
        "USER": config("MYSQL_USER"),
        "PASSWORD": config("MYSQL_PASSWORD"),
        "HOST": config("MYSQL_HOST"),
        "PORT": "3306",
    }
}

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    },
}
