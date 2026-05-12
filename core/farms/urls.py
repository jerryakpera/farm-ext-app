"""
URL configuration for the farms app.
"""

# django_packages
from django.urls import path

# app_packages
from . import views


app_name = "farms"


urlpatterns = [
    path(
        "all/",
        views.all_farms_list_view,
        name="all_farms_list",
    ),
    path(
        "farmer/farms/",
        views.farm_list_view,
        name="farm_list",
    ),
    path(
        "farmer/farms/create/",
        views.farm_create_view,
        name="farm_create",
    ),
    path(
        "farmer/farms/<int:farm_id>/",
        views.farm_detail_view,
        name="farm_detail",
    ),
    path(
        "farmer/farms/<int:farm_id>/edit/",
        views.farm_edit_view,
        name="farm_edit",
    ),
    path(
        "farmer/farms/<int:farm_id>/delete/", views.farm_delete_view, name="farm_delete"
    ),
    path(
        "farmer/farms/<int:farm_id>/images/",
        views.farm_image_upload_view,
        name="farm_image_upload",
    ),
    path(
        "farms/<int:farm_id>/verify/",
        views.farm_verify_view,
        name="farm_verify",
    ),
]
