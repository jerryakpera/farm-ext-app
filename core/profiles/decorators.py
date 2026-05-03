"""
Decorators for the `profiles` app.
"""

# python_packages
from functools import wraps

# django_packages
from django.contrib import messages
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
            messages.error(request, "Access restricted to farmers only.")
            return redirect("home")
        return view_func(request, *args, **kwargs)

    return wrapper
