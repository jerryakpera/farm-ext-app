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
    # ------------------------------------------------------------------
    # 7.3 Farmers & Farms
    # ------------------------------------------------------------------
    path("farmers/by-lga/", views.FarmersByLgaView.as_view(), name="farmers-by-lga"),
    path("farms/by-lga/", views.FarmsByLgaView.as_view(), name="farms-by-lga"),
    path(
        "farms/verification-status/",
        views.FarmVerificationStatusView.as_view(),
        name="farms-verification-status",
    ),
    path(
        "farms/primary-crops/",
        views.FarmsPrimaryCropsView.as_view(),
        name="farms-primary-crops",
    ),
    path(
        "farms/registration-trend/",
        views.FarmsRegistrationTrendView.as_view(),
        name="farms-registration-trend",
    ),
]
