"""
Models for the visits app.
"""

# django_packages
from django.db import models

# other_apps_packages
from core.farms.models import Farm
from core.profiles.models import ExtensionAgentProfile


class FarmVisit(models.Model):
    """
    Records a physical visit made by an extension agent to a registered farm.

    Visit logs serve two purposes: they provide a traceable history of
    agent activity across LGAs, and they feed into the farm verification
    workflow — an agent can only verify a farm after logging a visit that
    confirms the physical farm matches the virtual farm profile.

    If a follow-up is required, follow_up_date should be set to give the
    agent a clear target date for the next interaction.
    """

    agent = models.ForeignKey(
        ExtensionAgentProfile,
        on_delete=models.CASCADE,
        related_name="farm_visits",
    )
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="visits",
    )
    visit_date = models.DateField()
    purpose = models.CharField(
        max_length=255,
        help_text="Brief description of the reason for the visit.",
    )
    observations = models.TextField(
        blank=True,
        help_text="What the agent observed during the visit.",
    )
    recommendations = models.TextField(
        blank=True,
        help_text="Advice or action points given to the farmer.",
    )
    follow_up_required = models.BooleanField(
        default=False,
        help_text="Indicates whether a follow-up visit is needed.",
    )
    follow_up_date = models.DateField(
        null=True,
        blank=True,
        help_text="Target date for the follow-up visit, if required.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Farm Visit"
        verbose_name_plural = "Farm Visits"
        ordering = ["-visit_date"]

    def __str__(self):
        return f"Visit to {self.farm.name} by {self.agent.user.full_name} on {self.visit_date}"
