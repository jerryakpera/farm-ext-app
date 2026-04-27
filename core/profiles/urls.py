"""
URL configuration for the accounts app.
"""

# django_packages
from django.contrib.auth import views as auth_views
from django.urls import path

# other_apps_packages
from core.farms.forms import FarmDetailsForm

# app_packages
from .forms import ProfileBioForm, RoleSelectionForm
from .views import RegistrationWizardView


app_name = "accounts"

# The form list is passed directly to as_view() so the URL conf owns
# the wizard's form sequence rather than the view class, keeping the
# view reusable if a different step order is ever needed.
WIZARD_FORMS = [
    ("role_selection", RoleSelectionForm),
    ("profile_bio", ProfileBioForm),
    ("farm_details", FarmDetailsForm),
]

urlpatterns = [
    # --- Registration wizard ---
    path(
        "register/",
        RegistrationWizardView.as_view(WIZARD_FORMS),
        name="register",
    ),
    # --- Login ---
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    # --- Logout ---
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="accounts:login",
        ),
        name="logout",
    ),
    # --- Password change ---
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url="/accounts/password/change/done/",
        ),
        name="password_change",
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html",
        ),
        name="password_change_done",
    ),
]
