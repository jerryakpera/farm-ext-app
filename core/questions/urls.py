"""
URL configuration for the questions app.
"""

# django_packages
from django.urls import path

# app_packages
from . import views


app_name = "questions"

urlpatterns = [
    path("", views.question_list_view, name="question_list"),
    path("ask/", views.ask_question_view, name="ask_question"),
    path("<int:question_id>/", views.question_detail_view, name="question_detail"),
    path("<int:question_id>/edit/", views.edit_question_view, name="edit_question"),
    path(
        "<int:question_id>/delete/", views.delete_question_view, name="delete_question"
    ),
]
