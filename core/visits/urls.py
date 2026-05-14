"""
URL configuration for the visits app.
"""

# django_packages
from django.urls import path

# app_packages
from . import views


app_name = "visits"

urlpatterns = [
    # --- Core visit URLs ---
    path("log/", views.log_visit_view, name="log"),
    path("", views.visit_list_view, name="list"),
    path("<int:pk>/", views.visit_detail_view, name="detail"),
    path("<int:pk>/edit/", views.edit_visit_view, name="edit"),
    path("<int:pk>/delete/", views.delete_visit_view, name="delete"),
    path("farm/<int:farm_pk>/", views.farm_visits_view, name="farm_visits"),
    # --- Visit-level child records ---
    path(
        "<int:visit_pk>/issue/add/", views.add_visit_issue_view, name="add_visit_issue"
    ),
    path("<int:pk>/media/", views.add_visit_media_view, name="add_visit_media"),
    path(
        "<int:pk>/follow-up/", views.add_visit_followup_view, name="add_visit_followup"
    ),
    path(
        "<int:pk>/feedback/", views.add_farmer_feedback_view, name="add_farmer_feedback"
    ),
    # --- Crop analysis ---
    path(
        "<int:visit_pk>/crop-analysis/add/",
        views.add_crop_analysis_view,
        name="add_crop_analysis",
    ),
    path(
        "<int:visit_pk>/crop-analysis/<int:pk>/",
        views.crop_analysis_detail_view,
        name="crop_analysis_detail",
    ),
    path(
        "crop-analysis/<int:analysis_pk>/issue/add/",
        views.add_crop_issue_view,
        name="add_crop_issue",
    ),
    path(
        "crop-analysis/<int:analysis_pk>/action/add/",
        views.add_crop_action_view,
        name="add_crop_action",
    ),
    path(
        "crop-analysis/<int:analysis_pk>/pest/add/",
        views.add_pest_incidence_view,
        name="add_pest_incidence",
    ),
    # --- Livestock analysis ---
    path(
        "<int:visit_pk>/livestock-analysis/add/",
        views.add_livestock_analysis_view,
        name="add_livestock_analysis",
    ),
    path(
        "<int:visit_pk>/livestock-analysis/<int:pk>/",
        views.livestock_analysis_detail_view,
        name="livestock_analysis_detail",
    ),
    path(
        "livestock-analysis/<int:analysis_pk>/issue/add/",
        views.add_livestock_issue_view,
        name="add_livestock_issue",
    ),
    path(
        "livestock-analysis/<int:analysis_pk>/action/add/",
        views.add_livestock_action_view,
        name="add_livestock_action",
    ),
    path(
        "livestock-analysis/<int:analysis_pk>/disease/add/",
        views.add_livestock_disease_view,
        name="add_livestock_disease",
    ),
]
