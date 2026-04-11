"""
Celery application entry point for PS119.
"""

# python_packages
import os

# other_apps_packages
from celery import Celery

# The settings module is set before anything Django-related is imported.
# local.py is used when DEBUG=True, production.py otherwise.
# This mirrors your existing pattern exactly.
from config.settings import base


if base.DEBUG:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "config.settings.local",
    )
else:  # pragma: no cover
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "config.settings.production",
    )


app = Celery("config")

# All Celery config lives in Django settings under the CELERY_ namespace.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in every INSTALLED_APP.
app.autodiscover_tasks()
