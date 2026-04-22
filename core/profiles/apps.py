# django_packages
from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    """
    Configurations for the ProfileConfig.
    """

    name = "core.profiles"

    def ready(self):
        """
        Import signal handlers when the app is ready.
        """

        # other_apps_packages
        import core.profiles.signals
