"""
Management command to seed common Plateau State crops into the Crop table.

Usage:
    python manage.py seed_crops
    python manage.py seed_crops --reverse
"""

# django_packages
from django.core.management.base import BaseCommand

# other_apps_packages
from core.farms.constants import PLATEAU_CROPS
from core.farms.models import Crop


class Command(BaseCommand):
    """
    Command to seed the Crop table with common Plateau State crops.
    """

    help = "Seeds the Crop table with common crops grown in Plateau State."

    def add_arguments(self, parser):
        """
        Define command-line arguments for the management command.

        Parameters
        ----------
        parser : ArgumentParser
            The argument parser used to define command options.
        """

        parser.add_argument(
            "--reverse",
            action="store_true",
            help="Remove all seeded crops from the database.",
        )

    def handle(self, *args, **options):
        """
        Execute the management command logic.

        Parameters
        ----------
        *args
            Positional arguments passed to the command.
        **options
            Command-line options parsed by Django.
        """

        if options["reverse"]:
            deleted_count, _ = Crop.objects.filter(name__in=PLATEAU_CROPS).delete()
            self.stdout.write(self.style.WARNING(f"Removed {deleted_count} crops."))
            return

        created_count = 0
        skipped_count = 0

        for name in PLATEAU_CROPS:
            _, created = Crop.objects.get_or_create(name=name)
            if created:
                created_count += 1
            else:
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created_count} crops created, {skipped_count} already existed."
            )
        )
