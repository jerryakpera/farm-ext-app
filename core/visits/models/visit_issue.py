"""
Models for the visits app.
"""

# django_packages
from django.db import models

# app_packages
from .choices import Severity
from .visit import Visit


class VisitIssue(models.Model):
    """
    Problems identified during a farm visit.
    """

    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name="issues",
        help_text="The visit this issue was identified in.",
    )

    title = models.CharField(
        max_length=255,
        help_text="A short title describing the issue found during the visit.",
    )

    description = models.TextField(
        blank=True,
        help_text="A detailed explanation of the issue, if needed.",
    )

    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.MEDIUM,
        help_text="How serious the issue is, from low to critical.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The date and time when this issue was recorded."
    )

    def __str__(self):
        return f"Issue ({self.severity}) for Visit #{self.visit_id}"
