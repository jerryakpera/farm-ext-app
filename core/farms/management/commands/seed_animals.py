"""
Management command to seed common Plateau State animals into the Animal table.
"""

# django_packages
from django.core.management.base import BaseCommand

# other_apps_packages
from core.farms.constants import FARM_ANIMALS
from core.farms.models import Animal


class Command(BaseCommand):
    """
    Command to generate the LGAs for the project.
    """

    help = "Seeds the Animal table with common animals kept in Plateau State."

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
            help="Remove all seeded animals from the database.",
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
            deleted_count, _ = Animal.objects.filter(name__in=FARM_ANIMALS).delete()
            self.stdout.write(self.style.WARNING(f"Removed {deleted_count} animals."))
            return

        created_count = skipped_count = 0
        for name in FARM_ANIMALS:
            _, created = Animal.objects.get_or_create(name=name)
            if created:
                created_count += 1
            else:
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created_count} animals created, {skipped_count} already existed."
            )
        )
