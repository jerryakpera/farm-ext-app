"""
Context processors for the notifications app.
"""


def notifications(request):
    """
    Provide notification context data for templates.

    Returns unread notification counts and a limited list of recent unread
    notifications for authenticated users. Anonymous users receive an empty
    context.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    dict
        Context dictionary containing unread notification count and recent
        notifications, or an empty dict for unauthenticated users.
    """

    if not request.user.is_authenticated:
        return {}

    qs = request.user.notifications.filter(is_read=False).order_by("-created_at")[:5]

    return {
        "unread_notification_count": request.user.notifications.filter(
            is_read=False
        ).count(),
        "recent_notifications": qs,
    }
