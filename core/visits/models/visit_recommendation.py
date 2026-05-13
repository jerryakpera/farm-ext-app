"""
Models for the visits app.
"""

# django_packages
from django.db import models

# app_packages
from .visit import Visit


class VisitRecommendation(models.Model):
    """
    Advice or action points given during a visit.
    """

    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name="recommendations",
        help_text="The visit this recommendation belongs to.",
    )

    recommendation = models.TextField(
        help_text="Advice or action steps given to the farmer during the visit.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when this recommendation was recorded.",
    )

    def __str__(self):
        return f"Recommendation for Visit #{self.visit_id}"
