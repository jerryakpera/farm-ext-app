"""
URL configuration for the analytics app.
"""

# django_packages
from django.urls import path

# app_packages
from .views import DashboardAuthCheckView


app_name = "analytics_api"

urlpatterns = [
    path("auth/check/", DashboardAuthCheckView.as_view(), name="auth_check"),
]
