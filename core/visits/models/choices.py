"""
Choices for the `visit` models.
"""

# django_packages
from django.db import models


class Severity(models.TextChoices):
    """
    Indicates the level of seriousness of an issue or condition.
    """

    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"
