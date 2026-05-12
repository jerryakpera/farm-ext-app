"""
Signals for the `notifications` app.
"""

# django_packages
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

# other_apps_packages
from core.notifications.models import Notification
from core.notifications.utils import notify
from core.profiles.models import ExtensionAgentProfile
from core.questions.models import AnswerHelpfulness, Question


@receiver(post_save, sender=Question)
def notify_agents_of_new_question(sender, instance, created, **kwargs):
    """
    Send notifications to all extension agents when a new question is created.

    Parameters
    ----------
    sender : type
        The model class that sent the signal.
    instance : Question
        The newly created Question instance.
    created : bool
        Indicates whether the instance was created.
    **kwargs : dict
        Additional signal keyword arguments.
    """

    if not created:
        return
    link = reverse("questions:question_detail", args=[instance.pk])
    for agent_profile in ExtensionAgentProfile.objects.select_related("user"):
        notify(
            recipient=agent_profile.user,
            kind=Notification.Kind.NEW_QUESTION,
            message=f'A new question was posted: "{instance.title}"',
            link=link,
        )


@receiver(post_save, sender=AnswerHelpfulness)
def notify_agent_of_helpfulness(sender, instance, created, **kwargs):
    """
    Notify an agent when their answer is marked helpful or not helpful.

    Parameters
    ----------
    sender : type
        The model class that sent the signal.
    instance : AnswerHelpfulness
        The AnswerHelpfulness instance being saved.
    created : bool
        Indicates whether the instance was newly created.
    **kwargs : dict
        Additional signal keyword arguments.
    """

    if not created:
        return

    link = reverse("questions:question_detail", args=[instance.answer.question.pk])

    if instance.is_helpful:
        kind = Notification.Kind.ANSWER_HELPFUL
        message = (
            f'Your answer on "{instance.answer.question.title}" was marked helpful.'
        )
    else:
        kind = Notification.Kind.ANSWER_NOT_HELPFUL
        message = (
            f'Your answer on "{instance.answer.question.title}" was marked not helpful.'
        )

    notify(
        recipient=instance.answer.agent.user,
        kind=kind,
        message=message,
        link=link,
    )
