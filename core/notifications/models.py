"""
Models for the `notifications` model.
"""

# django_packages
from django.db import models

# other_apps_packages
from core.custom_user.models import User


class Notification(models.Model):
    """
    Stores a notification sent to a user within the platform.
    """

    class Kind(models.TextChoices):
        """
        Defines the different types of notifications supported.
        """

        NEW_QUESTION = "new_question", "New question"
        NEW_ANSWER = "new_answer", "New answer"
        ANSWER_HELPFUL = "answer_helpful", "Answer marked helpful"
        ANSWER_NOT_HELPFUL = "answer_not_helpful", "Answer marked not helpful"

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    kind = models.CharField(max_length=30, choices=Kind.choices)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
