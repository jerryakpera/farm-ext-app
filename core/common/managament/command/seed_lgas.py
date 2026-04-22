"""
Management command to seed all 17 Plateau State LGAs into the LGA table.

Usage:
    python manage.py seed_lgas
    python manage.py seed_lgas --reverse
"""

# django_packages
from django.core.management.base import BaseCommand

# other_apps_packages
from core.common.constants import PLATEAU_LGAS
from core.common.models import LGA


class Command(BaseCommand):
    """
    Command to generate the LGAs for the project.
    """

    help = "Seeds the LGA table with all 17 Plateau State LGAs."

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
            help="Remove all seeded Plateau State LGAs from the database.",
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
            deleted_count, _ = LGA.objects.filter(state="Plateau").delete()
            self.stdout.write(
                self.style.WARNING(f"Removed {deleted_count} Plateau State LGAs.")
            )
            return

        created_count = 0
        skipped_count = 0

        for name in PLATEAU_LGAS:
            _, created = LGA.objects.get_or_create(
                name=name,
                defaults={"state": "Plateau"},
            )
            if created:
                created_count += 1
            else:
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created_count} LGAs created, {skipped_count} already existed."
            )
        )
