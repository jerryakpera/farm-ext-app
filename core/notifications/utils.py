"""
Utility functions for the `notifications` app.
"""

# app_packages
from .models import Notification


def notify(recipient, kind, message, link=""):
    """
    Create and persist a notification for a user.

    Parameters
    ----------
    recipient : User
        The user who will receive the notification.
    kind : str
        The type of notification (must match Notification.Kind choices).
    message : str
        The notification message content.
    link : str, optional
        Optional URL or path associated with the notification.

    Returns
    -------
    Notification
        The created Notification instance.
    """

    Notification.objects.create(
        recipient=recipient,
        kind=kind,
        message=message,
        link=link,
    )
