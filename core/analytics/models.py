"""
Models for the analytics app.
"""

# django_packages
from django.db import models

# other_apps_packages
from core.custom_user.models import User


class DashboardWhitelist(models.Model):
    """
    Holds the emails of people permitted to register as on the dashboard platform.
    """

    email = models.EmailField(unique=True)
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dashboard_whitelist_entries",
        help_text="Admin user who added this entry.",
    )
    date_added = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(
        default=False,
        help_text="Set to True once the whitelisted email completes registration.",
    )

    class Meta:
        verbose_name = "Dashboard Whitelist"
        verbose_name_plural = "Dashboard Whitelist"

    def __str__(self):
        """
        Return the string representation of the whitelist entry.

        Returns
        -------
        str
            The whitelisted email address.
        """

        return self.email
