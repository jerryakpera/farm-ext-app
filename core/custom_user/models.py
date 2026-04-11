"""
Models for the `user` app.
"""

# third_party_packages
from django_use_email_as_username.models import BaseUser, BaseUserManager


class User(BaseUser):
    """
    Custom user model extending BaseUser.
    """

    objects = BaseUserManager()
