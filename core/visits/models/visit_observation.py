"""
Models for the visits app.
"""

# django_packages
from django.db import models

# app_packages
from .visit import Visit


class VisitObservation(models.Model):
    """
    Raw observations recorded during a visit.
    """

    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name="observations",
        help_text="The visit this observation belongs to.",
    )

    observation = models.TextField(
        help_text="A detailed note describing what was observed during the visit.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time this observation was recorded.",
    )

    def __str__(self):
        return f"Observation for Visit #{self.visit_id}"
