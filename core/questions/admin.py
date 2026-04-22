"""
Admin configuration for the questions app.
"""

# django_packages
from django.contrib import admin

# app_packages
from .models import (
    Answer,
    AnswerHelpfulness,
    AnswerImage,
    Escalation,
    Question,
    QuestionImage,
)


class QuestionImageInline(admin.TabularInline):
    """
    Inline admin for QuestionImage.
    Displays attached images within the Question detail page.
    """

    model = QuestionImage
    extra = 1
    readonly_fields = ("uploaded_at",)


class AnswerImageInline(admin.TabularInline):
    """
    Inline admin for AnswerImage.
    Displays attached images within the Answer detail page.
    """

    model = AnswerImage
    extra = 1
    readonly_fields = ("uploaded_at",)


class AnswerInline(admin.TabularInline):
    """
    Inline admin for Answer.
    Allows answers to be reviewed directly on the Question detail page.
    """

    model = Answer
    extra = 0
    readonly_fields = ("agent", "created_at", "updated_at")
    show_change_link = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Question model.

    Displays question status and escalation state with filtering support.
    Answers and images are accessible inline.
    """

    inlines = [QuestionImageInline, AnswerInline]
    list_display = (
        "title",
        "farmer",
        "crop_concern",
        "status",
        "is_escalated",
        "created_at",
    )
    list_filter = ("status", "is_escalated", "crop_concern")
    search_fields = ("title", "body", "farmer__user__full_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Answer model.

    Displays answers with their associated questions and agents.
    Answer images are accessible inline.
    """

    inlines = [AnswerImageInline]
    list_display = ("question", "agent", "created_at")
    search_fields = ("question__title", "agent__user__full_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AnswerHelpfulness)
class AnswerHelpfulnessAdmin(admin.ModelAdmin):
    """
    Admin configuration for the AnswerHelpfulness model.

    Read-only view of farmer feedback on answers.
    """

    list_display = ("answer", "farmer", "is_helpful", "created_at")
    list_filter = ("is_helpful",)
    readonly_fields = ("answer", "farmer", "is_helpful", "created_at")


@admin.register(Escalation)
class EscalationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Escalation model.

    Displays all escalated questions with the responsible agent and reason.
    """

    list_display = ("question", "escalated_by", "escalated_at")
    search_fields = ("question__title", "escalated_by__user__full_name")
    readonly_fields = ("escalated_at",)
