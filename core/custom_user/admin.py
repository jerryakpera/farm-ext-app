"""
Django admin configuration for the user model.
"""

# django_packages
from django.contrib import admin

# third_party_packages
from django_use_email_as_username.admin import BaseUserAdmin

# app_packages
from .models import User


admin.site.register(User, BaseUserAdmin)
