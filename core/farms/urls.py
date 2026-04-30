"""
URL configuration for the farms app.
"""

# django_packages
from django.urls import path

# app_packages
# local_packages
from .views import (
    farm_create_view,
    farm_delete_view,
    farm_detail_view,
    farm_edit_view,
    farm_image_upload_view,
    farm_list_view,
)


urlpatterns = [
    path(
        "farmer/farms/",
        farm_list_view,
        name="farm-list",
    ),
    path(
        "farmer/farms/create/",
        farm_create_view,
        name="farm-create",
    ),
    path(
        "farmer/farms/<int:farm_id>/",
        farm_detail_view,
        name="farm-detail",
    ),
    path(
        "farmer/farms/<int:farm_id>/edit/",
        farm_edit_view,
        name="farm-edit",
    ),
    path("farmer/farms/<int:farm_id>/delete/", farm_delete_view, name="farm-delete"),
    path(
        "farmer/farms/<int:farm_id>/images/",
        farm_image_upload_view,
        name="farm-image-upload",
    ),
]
