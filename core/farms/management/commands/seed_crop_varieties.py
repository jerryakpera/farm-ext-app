"""
Management command to seed crop varieties into the CropVariety table.

Only varieties whose parent crop already exists in the Crop table will
be seeded. Run seed_crops first if the Crop table is empty.

Usage:
    python manage.py seed_crop_varieties
    python manage.py seed_crop_varieties --reverse
"""

# django_packages
from django.core.management.base import BaseCommand

# other_apps_packages
from core.farms.constants import CROP_VARIETIES
from core.farms.models import Crop, CropVariety


class Command(BaseCommand):
    """
    Command to seed the CropVariety table with known varieties per crop.
    """

    help = "Seeds the CropVariety table with varieties for each seeded crop."

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
            help="Remove all seeded crop varieties from the database.",
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
            all_variety_names = [
                name for varieties in CROP_VARIETIES.values() for name in varieties
            ]
            deleted_count, _ = CropVariety.objects.filter(
                name__in=all_variety_names
            ).delete()
            self.stdout.write(
                self.style.WARNING(f"Removed {deleted_count} crop varieties.")
            )
            return

        created_count = 0
        skipped_count = 0
        missing_crops = []

        for crop_name, varieties in CROP_VARIETIES.items():
            try:
                crop = Crop.objects.get(name=crop_name)
            except Crop.DoesNotExist:
                missing_crops.append(crop_name)
                continue

            for variety_name in varieties:
                _, created = CropVariety.objects.get_or_create(
                    crop=crop,
                    name=variety_name,
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created_count} varieties created, "
                f"{skipped_count} already existed."
            )
        )

        if missing_crops:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped {len(missing_crops)} crop(s) not found in the database: "
                    + ", ".join(missing_crops)
                    + ". Run seed_crops first."
                )
            )
