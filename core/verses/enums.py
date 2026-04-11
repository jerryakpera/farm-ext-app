"""
Enums for the `verses` app.
"""

# django_packages
from django.db import models


class BibleVersion(models.TextChoices):
    """
    Choice lists for the version field.
    """

    WEB = "ENGWEBP", "World English Bible"
    KJV = "eng_kjv", "King James Version"
