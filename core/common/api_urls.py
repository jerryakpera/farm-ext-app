"""
URL configuration for the common app — API views.
"""

# django_packages
from django.urls import path

# app_packages
from . import views


app_name = "common_api"

urlpatterns = [
    path(
        "wards/",
        views.WardListView.as_view(),
        name="ward_list",
    ),
    path(
        "lgas/<int:lga_id>/wards/",
        views.WardsByLGAView.as_view(),
        name="wards_by_lga",
    ),
]
