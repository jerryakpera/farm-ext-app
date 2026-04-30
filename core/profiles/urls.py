"""
URL configuration for the accounts app.
"""

# django_packages
from django.contrib.auth import views as auth_views
from django.urls import path

# other_apps_packages
from core.farms.forms import FarmDetailsForm
from core.profiles.decorators import guest_only

# app_packages
from . import views
from .forms import ProfileBioForm, RoleSelectionForm


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
        views.RegistrationWizardView.as_view(WIZARD_FORMS),
        name="register",
    ),
    # --- Login ---
    path(
        "login/",
        guest_only(
            auth_views.LoginView.as_view(
                template_name="profiles/pages/login.html",
                redirect_authenticated_user=True,
            )
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
    path(
        "farmer/profile/",
        view=views.farmer_profile_view,
        name="farmer-profile",
    ),
]
