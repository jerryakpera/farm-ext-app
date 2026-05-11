"""
Management command to seed all 17 Plateau State LGAs and their wards.

Usage:
    python manage.py seed_lgas
    python manage.py seed_lgas --reverse
"""

# django_packages
from django.core.management.base import BaseCommand

# other_apps_packages
from core.common.constants import PLATEAU_LGA_WARDS, PLATEAU_LGAS
from core.common.models import LGA, Ward


class Command(BaseCommand):
    """
    Command to seed LGAs and wards for the project.
    """

    help = (
        "Seeds the LGA and Ward tables with all 17 Plateau State LGAs and their wards."
    )

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
            help="Remove all seeded Plateau State LGAs and their wards from the database.",
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
            lgas = LGA.objects.filter(state="Plateau")
            ward_count, _ = Ward.objects.filter(lga__in=lgas).delete()
            lga_count, _ = lgas.delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Removed {lga_count} Plateau State LGAs and {ward_count} wards."
                )
            )
            return

        lgas_created = lgas_skipped = wards_created = wards_skipped = 0

        for lga_name in PLATEAU_LGAS:
            lga, created = LGA.objects.get_or_create(
                name=lga_name,
                defaults={"state": "Plateau"},
            )

            if created:
                lgas_created += 1
            else:
                lgas_skipped += 1

            for ward_name in PLATEAU_LGA_WARDS.get(lga_name, []):
                _, ward_created = Ward.objects.get_or_create(
                    name=ward_name,
                    lga=lga,
                )

                if ward_created:
                    wards_created += 1
                else:
                    wards_skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. "
                f"{lgas_created} LGAs created, {lgas_skipped} already existed. "
                f"{wards_created} wards created, {wards_skipped} already existed."
            )
        )
