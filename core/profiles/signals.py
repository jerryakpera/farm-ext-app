"""
Signals for the accounts app.
"""

# django_packages
from django.db.models.signals import post_save
from django.dispatch import receiver

# other_apps_packages
from core.custom_user.models import User

# app_packages
from .models import ExtensionAgentProfile, FarmerProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a corresponding profile when a new user is created.

    Parameters
    ----------
    sender : type
        The model class that sent the signal.
    instance : User
        The actual instance being saved.
    created : bool
        Indicates whether this is a newly created instance.
    **kwargs
        Additional keyword arguments passed by the signal.
    """

    if not created or not instance.role:
        return

    if instance.role == User.Role.FARMER:
        FarmerProfile.objects.get_or_create(user=instance)

    elif instance.role == User.Role.EXTENSION_AGENT:
        ExtensionAgentProfile.objects.get_or_create(user=instance)
