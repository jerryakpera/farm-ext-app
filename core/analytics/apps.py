"""
App configuration for the analytics app.
"""

# django_packages
from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """
    Configure the analytics app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "core.analytics"
