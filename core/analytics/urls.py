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
    # ------------------------------------------------------------------
    # 7.4 Visits
    # ------------------------------------------------------------------
    path(
        "visits/by-purpose/",
        views.VisitsByPurposeView.as_view(),
        name="visits-by-purpose",
    ),
    path(
        "visits/by-outcome/",
        views.VisitsByOutcomeView.as_view(),
        name="visits-by-outcome",
    ),
    path("visits/trend/", views.VisitTrendView.as_view(), name="visits-trend"),
    path("visits/by-agent/", views.VisitsByAgentView.as_view(), name="visits-by-agent"),
    path("visits/by-lga/", views.VisitsByLgaView.as_view(), name="visits-by-lga"),
    path(
        "visits/follow-up-rate/",
        views.VisitFollowUpRateView.as_view(),
        name="visits-follow-up-rate",
    ),
    path(
        "visits/priority-level/",
        views.VisitsByPriorityView.as_view(),
        name="visits-priority-level",
    ),
]
