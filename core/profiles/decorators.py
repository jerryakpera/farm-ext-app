"""
Decorators for the `profiles` app.
"""

# python_packages
from functools import wraps

# django_packages
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def guest_only(view_func):
    """
    Restrict access to guest-only pages for authenticated users.

    Parameters
    ----------
    view_func : callable
        The view function to be wrapped.

    Returns
    -------
    callable
        The wrapped view function that redirects authenticated users.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        """
        Execute the wrapped view with guest-only access control.

        Parameters
        ----------
        request : HttpRequest
            The incoming HTTP request.
        *args
            Positional arguments passed to the view.
        **kwargs
            Keyword arguments passed to the view.

        Returns
        -------
        HttpResponse
            Redirect response for authenticated users or the original view response.
        """
        if request.user.is_authenticated:
            return redirect("common:index")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def farmer_required(view_func):
    """
    Decorator that restricts access to views to users with the farmer role.

    Parameters
    ----------
    view_func : callable
        The view function being wrapped.

    Returns
    -------
    callable
        The wrapped view function that enforces farmer-only access.
    """

    def wrapper(request, *args, **kwargs):
        """
        Inner wrapper that enforces authentication and role-based access control.

        Parameters
        ----------
        request : HttpRequest
            The incoming HTTP request.
        *args
            Positional arguments passed to the view.
        **kwargs
            Keyword arguments passed to the view.

        Returns
        -------
        HttpResponse
            Redirects to login or home if unauthorized, otherwise executes the view.
        """

        if not request.user.is_authenticated:
            return redirect("login")

        if not request.user.is_farmer:
            messages.error(
                request=request,
                message="Access restricted to farmers only.",
            )

            return redirect("common:index")

        return view_func(request, *args, **kwargs)

    return wrapper


def agent_required(view_func):
    """
    Restrict a view to authenticated extension agents only.

    Unauthenticated users are redirected to the login page.
    Authenticated non-agents receive a 403.

    Parameters
    ----------
    view_func : callable
        The view function to wrap.

    Returns
    -------
    callable
        The wrapped view function.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        """
        Execute the wrapped view with agent-only access control.

        Parameters
        ----------
        request : HttpRequest
            The incoming HTTP request.
        *args
            Positional arguments passed to the view.
        **kwargs
            Keyword arguments passed to the view.

        Returns
        -------
        HttpResponse
            Redirects unauthenticated users, raises 403 for non-agents,
            otherwise returns the view response.
        """

        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        if not request.user.is_agent:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper
