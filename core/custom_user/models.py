"""
Models for the `user` app.
"""

# django_packages
from django.db import models

# third_party_packages
from django_use_email_as_username.models import BaseUser, BaseUserManager


class User(BaseUser):
    """
    Custom user model. Email is used as the login identifier via BaseUser.
    """

    class Role(models.TextChoices):
        """
        Enumeration of user roles within the system.
        """

        FARMER = "farmer", "Farmer"
        EXTENSION_AGENT = "extension_agent", "Extension Agent"
        EXPERT = "expert", "Expert"

    objects = BaseUserManager()

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        null=True,
        blank=True,
    )
    phone_number = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        """
        Return the string representation of the user.

        Returns
        -------
        str
            The user's full name and email.
        """

        return self.full_name

    @property
    def is_farmer(self):
        """
        Determine whether the user has the farmer role.

        Returns
        -------
        bool
            True if the user is a farmer, otherwise False.
        """

        return self.role == self.Role.FARMER

    @property
    def is_agent(self):
        """
        Determine whether the user has the extension agent role.

        Returns
        -------
        bool
            True if the user is an extension agent, otherwise False.
        """

        return self.role == self.Role.EXTENSION_AGENT

    @property
    def full_name(self):
        """
        Return the user's full name.

        Returns
        -------
        str
            First and last name joined, or just first name if no last name is set.
        """

        if self.last_name:
            return f"{self.first_name} {self.last_name}"

        return self.first_name
