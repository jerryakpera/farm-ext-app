"""
URL configuration for the analytics app.
"""

# django_packages
from django.urls import path

# app_packages
from . import views


app_name = "analytics_api"

urlpatterns = [
    path(
        "overview/",
        views.OverviewView.as_view(),
        name="overview",
    ),
    path(
        "auth/check/",
        views.DashboardAuthCheckView.as_view(),
        name="auth_check",
    ),
]
