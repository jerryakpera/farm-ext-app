"""
Signals for the questions app.
"""

# django_packages
from django.db.models.signals import post_save
from django.dispatch import receiver

# app_packages
from .models import Answer, Escalation, Question


@receiver(post_save, sender=Answer)
def mark_question_as_answered(sender, instance, created, **kwargs):
    """
    When a new answer is posted, move the question to 'answered'
    unless it has already been escalated or closed.

    Parameters
    ----------
    sender : type
        The model class that sent the signal.
    instance : Answer
        The Answer instance that was saved.
    created : bool
        Indicates whether the instance was newly created.
    **kwargs
        Additional keyword arguments passed by the signal.
    """

    if not created:
        return

    question = instance.question
    if question.status == Question.Status.OPEN:
        question.status = Question.Status.ANSWERED
        question.save(update_fields=["status", "updated_at"])


@receiver(post_save, sender=Escalation)
def mark_question_as_escalated(sender, instance, created, **kwargs):
    """
    When an Escalation record is created, set the question's
    is_escalated flag and update its status to 'escalated'.

    Parameters
    ----------
    sender : type
        The model class that sent the signal.
    instance : Escalation
        The Escalation instance that was saved.
    created : bool
        Indicates whether the instance was newly created.
    **kwargs
        Additional keyword arguments passed by the signal.
    """

    if not created:
        return

    question = instance.question
    question.is_escalated = True
    question.status = Question.Status.ESCALATED
    question.save(update_fields=["is_escalated", "status", "updated_at"])
