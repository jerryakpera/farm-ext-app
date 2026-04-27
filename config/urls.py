"""
URL configuration for farm-ext project.
"""

# django_packages
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.common.urls")),
    path("", include("core.profiles.urls")),
]
