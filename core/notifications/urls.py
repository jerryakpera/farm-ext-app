"""
URL configuration for the `notifications` app.
"""

# django_packages
from django.urls import path

# app_packages
from . import views


app_name = "notifications"

urlpatterns = [
    path(
        "notifications/",
        views.notification_list_view,
        name="list",
    ),
    path(
        "notifications/<int:pk>/go/",
        views.notification_redirect_view,
        name="redirect",
    ),
]
