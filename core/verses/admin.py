"""
Django admin configuration for the `verses` app.
"""

# django_packages
from django.contrib import admin

# app_packages
from .models import MemoryVerse, SingleVerse


admin.site.register(SingleVerse)
admin.site.register(MemoryVerse)
