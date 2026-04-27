"""
URL configuration for the `common` app.
"""

# django_packages
from django.urls import path

# app_packages
from . import views


app_name = "common"


urlpatterns = [
    path(
        "",
        view=views.index,
        name="index",
    )
]
