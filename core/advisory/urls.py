"""
URL configuration for the advisory app.
"""

# django_packages
from django.urls import path

# app_packages
from . import views


app_name = "advisory"

urlpatterns = [
    path("", views.advisory_post_list_view, name="post_list"),
    path("my-posts/", views.my_advisory_posts_view, name="my_posts"),
    path("posts/create/", views.create_advisory_post_view, name="create_post"),
    path("posts/<int:post_id>/", views.advisory_post_detail_view, name="post_detail"),
    path("posts/<int:post_id>/edit/", views.edit_advisory_post_view, name="edit_post"),
    path("posts/<int:post_id>/publish/", views.publish_post_view, name="publish_post"),
    path(
        "posts/<int:post_id>/delete/",
        views.delete_advisory_post_view,
        name="delete_post",
    ),
    path(
        "posts/<int:post_id>/unpublish/",
        views.unpublish_post_view,
        name="unpublish_post",
    ),
]
