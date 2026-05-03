"""
Models for the questions app.
"""

# django_packages
from django.db import models

# other_apps_packages
from core.common import utils as common_utils, validators as common_validators
from core.farms.models import Farm
from core.profiles.models import ExtensionAgentProfile, FarmerProfile


class Question(models.Model):
    """
    A question posted by a farmer seeking agricultural advice.
    """

    class Status(models.TextChoices):
        """
        Status options for a question in the system.
        """

        OPEN = "open", "Open"
        ANSWERED = "answered", "Answered"
        ESCALATED = "escalated", "Escalated"
        CLOSED = "closed", "Closed"

    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    farm = models.ForeignKey(
        Farm,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
        help_text="The farm this question relates to, if applicable.",
    )
    image = models.ImageField(
        upload_to=common_utils.file_upload_path,
        validators=[
            common_validators.validate_image_size,
            common_validators.validate_image_format,
        ],
        null=True,
        blank=True,
        help_text="An optional image to help illustrate the question.",
    )

    title = models.CharField(max_length=255)
    body = models.TextField()
    crop_concern = models.ForeignKey(
        "farms.Crop",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
        help_text="The crop this question is about.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    is_escalated = models.BooleanField(
        default=False,
        help_text="Set to True when an agent escalates this question to an expert.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ["-created_at"]

    def __str__(self):
        """
        Return the string representation of a question.

        Returns
        -------
        str
            The question title and farmer's full name.
        """

        return f"{self.title} — {self.farmer.user}"


class Answer(models.Model):
    """
    An answer posted by an extension agent in response to a farmer's question.
    """

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    agent = models.ForeignKey(
        ExtensionAgentProfile,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    image = models.ImageField(
        upload_to=common_utils.file_upload_path,
        validators=[
            common_validators.validate_image_size,
            common_validators.validate_image_format,
        ],
        null=True,
        blank=True,
        help_text="An optional image to help illustrate the answer.",
    )

    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        ordering = ["created_at"]

    def __str__(self):
        """
        Return the string representation of an answer.

        Returns
        -------
        str
            The agent's full name and the related question title.
        """

        return f"Answer by {self.agent.user.full_name} on: {self.question.title}"


class AnswerHelpfulness(models.Model):
    """
    Records a farmer's helpfulness rating on a specific answer.
    """

    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="helpfulness_ratings",
    )
    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name="helpfulness_ratings",
    )
    is_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Answer Helpfulness"
        verbose_name_plural = "Answer Helpfulness Ratings"
        unique_together = ("answer", "farmer")

    def __str__(self):
        """
        Return the string representation of a feedback rating.

        Returns
        -------
        str
            A helpful/not helpful label, farmer name, and related answer ID.
        """

        rating = "Helpful" if self.is_helpful else "Not helpful"

        return f"{rating} — {self.farmer.user} on answer ID {self.answer.id}"


class Escalation(models.Model):
    """
    Records the escalation of a question by an extension agent.
    """

    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name="escalation",
    )
    escalated_by = models.ForeignKey(
        ExtensionAgentProfile,
        on_delete=models.CASCADE,
        related_name="escalations",
    )
    reason = models.TextField(
        help_text="The agent's explanation for why this question needs expert attention.",
    )
    escalated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Escalation"
        verbose_name_plural = "Escalations"
        ordering = ["-escalated_at"]

    def __str__(self):
        """
        Return the string representation of an escalation record.

        Returns
        -------
        str
            The title of the escalated question.
        """

        return f"Escalation for: {self.question.title}"
