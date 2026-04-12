"""
Django management command to create a superuser if none exists.
"""

# django_packages
from django.core.management.base import BaseCommand
from django.utils import timezone

# third_party_packages
from decouple import config

# other_apps_packages
from core.custom_user.models import User


class Command(BaseCommand):
    """
    Create a superuser if none exist.

    Example:
        manage.py createsuperuser_if_none_exists --user=admin --password=changeme
    """

    def handle(self, *args, **options):
        """
        Handle the command execution.

        Parameters
        ----------
        *args : tuple
            Positional arguments passed to the command.
        **options : dict
            Keyword arguments passed to the command.
        """

        if User.objects.exists():
            return

        email = config("SU_EMAIL")
        password = config("SU_PASSWORD")

        user = User.objects.create_superuser(
            email=email,
            password=password,
        )

        user.verified = True
        user.agreed_to_terms_at = timezone.now()
        user.save()

        self.stdout.write(f'User "{email}" was created')
