"""
URL configuration for the visits app.
"""

# django_packages
from django.urls import path

# app_packages
from . import views


app_name = "visits"

urlpatterns = [
    # path("log/", views.LogVisitView.as_view(), name="log"),
    # path("<int:pk>/", views.VisitDetailView.as_view(), name="detail"),
    # path("my-visits/", views.VisitListView.as_view(), name="list"),
    # path("farm/<int:farm_pk>/", views.FarmVisitsView.as_view(), name="farm_visits"),
    # path("<int:pk>/edit/", views.EditVisitView.as_view(), name="edit"),
    # path("<int:pk>/delete/", views.DeleteVisitView.as_view(), name="delete"),
]
