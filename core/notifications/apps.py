"""
Application configuration for the `notifications` app.
"""

# django_packages
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """
    Application configuration for the notifications app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "core.notifications"

    def ready(self):
        """
        Import signal handlers when the app is ready.

        This ensures that Django registers all signal receivers for the
        notifications app at startup.
        """

        # other_apps_packages
        import core.notifications.signals
