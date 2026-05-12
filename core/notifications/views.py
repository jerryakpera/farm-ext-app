"""
Views for the `notifications` app.
"""

# django_packages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

# app_packages
from .models import Notification


@login_required
def notification_list_view(request):
    """
    Display the authenticated user's notifications.

    All unread notifications are marked as read when the page is opened.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered notifications list page.
    """

    notifications = request.user.notifications.all()

    # Mark all as read when the page is opened
    request.user.notifications.filter(is_read=False).update(is_read=True)

    return render(
        request,
        "notifications/pages/notification_list.html",
        {
            "notifications": notifications,
        },
    )


@login_required
def notification_redirect_view(request, pk):
    """
    Mark a notification as read and redirect to its target link.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    pk : int
        The primary key of the notification.

    Returns
    -------
    HttpResponseRedirect
        Redirect to the notification link or notifications list page.
    """

    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user,
    )

    notification.is_read = True
    notification.save(update_fields=["is_read"])

    if notification.link:
        return redirect(notification.link)

    return redirect("notifications:list")
