"""
Models for the profiles app.
"""

# django_packages
from django.db import models

# other_apps_packages
# Create your models here.
from core.common.models import LGA
from core.custom_user.models import User


class ExtensionAgentWhitelist(models.Model):
    """
    Holds the emails of people permitted to register as extension agents.
    """

    email = models.EmailField(unique=True)
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="whitelist_entries",
        help_text="Admin user who added this entry.",
    )
    date_added = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(
        default=False,
        help_text="Set to True once the whitelisted email completes registration.",
    )

    class Meta:
        verbose_name = "Extension Agent Whitelist"
        verbose_name_plural = "Extension Agent Whitelist"

    def __str__(self):
        """
        Return the string representation of the whitelist entry.

        Returns
        -------
        str
            The whitelisted email address.
        """

        return self.email


class FarmerProfile(models.Model):
    """
    Extended profile for users with the Farmer role.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="farmer_profile",
    )
    lga = models.ForeignKey(
        LGA,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="farmers",
    )
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Farmer Profile"
        verbose_name_plural = "Farmer Profiles"

    def __str__(self):
        """
        Return the string representation of the farmer profile.

        Returns
        -------
        str
            The full name of the farmer.
        """

        return f"Farmer: {self.user.full_name}"


class ExtensionAgentProfile(models.Model):
    """
    Extended profile for users with the Extension Agent role.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="agent_profile",
    )
    staff_id = models.CharField(max_length=50, unique=True, blank=True)
    agency_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. ADP – Agricultural Development Programme",
    )
    assigned_lgas = models.ManyToManyField(
        LGA,
        blank=True,
        related_name="assigned_agents",
    )

    class Meta:
        verbose_name = "Extension Agent Profile"
        verbose_name_plural = "Extension Agent Profiles"

    def __str__(self):
        """
        Return the string representation of the extension agent profile.

        Returns
        -------
        str
            The full name of the extension agent.
        """

        return f"Agent: {self.user.full_name}"
