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
    # ------------------------------------------------------------------
    # 7.5 Questions & Answers
    # ------------------------------------------------------------------
    path(
        "questions/by-status/",
        views.QuestionsByStatusView.as_view(),
        name="questions-by-status",
    ),
    path("questions/trend/", views.QuestionTrendView.as_view(), name="questions-trend"),
    path(
        "questions/escalation-rate/",
        views.QuestionEscalationRateView.as_view(),
        name="questions-escalation-rate",
    ),
    path(
        "questions/answer-helpfulness/",
        views.AnswerHelpfulnessView.as_view(),
        name="questions-answer-helpfulness",
    ),
    path(
        "questions/top-crops/",
        views.TopCropsByQuestionsView.as_view(),
        name="questions-top-crops",
    ),
    # ------------------------------------------------------------------
    # 7.6 Advisory Posts
    # ------------------------------------------------------------------
    path(
        "advisory/by-type/",
        views.AdvisoryByTypeView.as_view(),
        name="advisory-by-type",
    ),
    path(
        "advisory/published-vs-draft/",
        views.AdvisoryPublishedVsDraftView.as_view(),
        name="advisory-published-vs-draft",
    ),
    path(
        "advisory/trend/",
        views.AdvisoryTrendView.as_view(),
        name="advisory-trend",
    ),
    # ------------------------------------------------------------------
    # 7.8 Geographic / Heatmap
    # ------------------------------------------------------------------
    path(
        "geo/farmers-by-lga/",
        views.GeoFarmersByLgaView.as_view(),
        name="geo-farmers-by-lga",
    ),
    path(
        "geo/farmers-by-ward/",
        views.GeoFarmersByWardView.as_view(),
        name="geo-farmers-by-ward",
    ),
    path(
        "geo/questions-by-lga/",
        views.GeoQuestionsByLgaView.as_view(),
        name="geo-questions-by-lga",
    ),
    path(
        "geo/crop-issues-by-lga/",
        views.GeoCropIssuesByLgaView.as_view(),
        name="geo-crop-issues-by-lga",
    ),
]
