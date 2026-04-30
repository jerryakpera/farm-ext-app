"""
Views for the accounts app.
"""

# django_packages
from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from django.shortcuts import redirect, render

# third_party_packages
from formtools.wizard.views import SessionWizardView

# other_apps_packages
from core.custom_user.models import User
from core.farms.forms import FarmDetailsForm
from core.farms.models import Farm, FarmerProfile

# app_packages
from .forms import FarmerProfileForm, ProfileBioForm, RoleSelectionForm
from .models import ExtensionAgentProfile, ExtensionAgentWhitelist


STEP_ROLE = "role_selection"
STEP_BIO = "profile_bio"
STEP_FARM = "farm_details"

FORMS = [
    (STEP_ROLE, RoleSelectionForm),
    (STEP_BIO, ProfileBioForm),
    (STEP_FARM, FarmDetailsForm),
]

TEMPLATES = {
    STEP_ROLE: "profiles/pages/register/step_role.html",
    STEP_BIO: "profiles/pages/register/step_bio.html",
    STEP_FARM: "profiles/pages/register/step_farm.html",
}


def _is_farmer(wizard):
    """
    Return True if the user selected the Farmer role in Step 1.

    Used as the condition_dict entry for the farm details step so that
    SessionWizardView skips it entirely for extension agents.

    Parameters
    ----------
    wizard : RegistrationWizardView
        The active wizard instance.

    Returns
    -------
    bool
        True when the selected role is FARMER, False otherwise.
    """

    step1 = wizard.get_cleaned_data_for_step(STEP_ROLE) or {}
    return step1.get("role") == User.Role.FARMER


class RegistrationWizardView(SessionWizardView):
    """
    Multi-step registration wizard.

    Step sequence:
    1. role_selection  — farmer or extension agent (both roles)
    2. profile_bio     — credentials + bio details  (both roles)
    3. farm_details    — farm and crop info          (farmers only)

    Step 3 is skipped entirely for extension agents via condition_dict.
    All records are created atomically in done() only after every applicable
    step has been validated.
    """

    form_list = FORMS
    condition_dict = {STEP_FARM: _is_farmer}

    def get_template_names(self):
        """
        Return the template path for the current step.

        Returns
        -------
        list[str]
            A single-item list containing the template path for the active step.
        """

        return [TEMPLATES[self.steps.current]]

    def get_form(self, step=None, data=None, files=None):
        """
        Return the form for the given step.

        For the profile_bio step, inject the role chosen in Step 1 onto the
        form instance as `selected_role` so that clean_email() can perform
        whitelist validation without needing access to the wizard itself.

        For the profile_bio step, also remove role-conditional fields that do
        not apply to the selected role so the template only renders relevant
        fields and required validation is not triggered for hidden ones.

        Parameters
        ----------
        step : str or None
            The step name. Defaults to the current step when None.
        data : QueryDict or None
            POST data for the step.
        files : MultiValueDict or None
            Uploaded files — unused in this wizard; kept for signature
            compatibility with the parent class.

        Returns
        -------
        forms.Form
            The prepared form instance for the requested step.
        """

        form = super().get_form(step, data, files)
        active_step = step or self.steps.current

        if active_step == STEP_BIO:
            step1_data = self.get_cleaned_data_for_step(STEP_ROLE) or {}
            role = step1_data.get("role")

            # Inject role so clean_email() can access it.
            form.selected_role = role

            if role == User.Role.FARMER:
                # Remove agent-only fields so they are neither rendered
                # nor validated.
                form.fields.pop("agency_name", None)
                form.fields.pop("staff_id", None)

            elif role == User.Role.EXTENSION_AGENT:
                # Remove farmer-only fields.
                form.fields.pop("lga", None)

        return form

    def get_context_data(self, form, **kwargs):
        """
        Add step metadata to the template context.

        Exposes `total_steps` so templates can render the correct step
        indicator without hard-coding the count (2 for agents, 3 for farmers).

        Parameters
        ----------
        form : forms.Form
            The current step's form instance.
        **kwargs : dict
            Additional context passed up the MRO.

        Returns
        -------
        dict
            Template context dictionary.
        """

        context = super().get_context_data(form=form, **kwargs)

        context["total_steps"] = self.steps.count
        context["current_step_num"] = self.steps.step1  # 1-based index

        return context

    # -----------------------------------------------------------------------
    # done()
    # -----------------------------------------------------------------------

    def done(self, form_list, **kwargs):
        """
        Called by SessionWizardView after all steps have been validated.

        Creates all records atomically:
        - User
        - FarmerProfile or ExtensionAgentProfile
        - Farm (farmers only)
        - Marks ExtensionAgentWhitelist.is_used = True (agents only)

        Logs the new user in and redirects to their role-specific dashboard.

        Parameters
        ----------
        form_list : list[forms.Form]
            Validated form instances for every completed step.
        **kwargs : dict
            Additional keyword arguments passed by the wizard.

        Returns
        -------
        HttpResponseRedirect
            Redirect to the appropriate dashboard.
        """

        step1 = self.get_cleaned_data_for_step(STEP_ROLE) or {}
        step2 = self.get_cleaned_data_for_step(STEP_BIO) or {}

        role = step1["role"]
        email = step2["email"].lower()

        # Guard against double-submission. If a User with this email was already
        # created (e.g. done() fired twice due to a browser retry), log them in
        # and redirect rather than attempting a duplicate insert.
        existing = User.objects.filter(email=email).first()
        if existing:
            login(self.request, existing)

            return redirect("common:index")

        with transaction.atomic():
            user = User.objects.create_user(
                email=email,
                password=step2["password"],
                first_name=step2["first_name"],
                last_name=step2["last_name"],
                phone_number=step2.get("phone_number", ""),
                role=role,
            )

            if role == User.Role.FARMER:
                step3 = self.get_cleaned_data_for_step(STEP_FARM) or {}
                self._create_farmer_records(user, step2, step3)

            elif role == User.Role.EXTENSION_AGENT:
                self._create_agent_records(user, step2)

        login(self.request, user)
        return redirect("common:index")

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _create_farmer_records(self, user, step2, step3):
        """
        Create FarmerProfile and Farm records for a newly registered farmer.

        Parameters
        ----------
        user : User
            The freshly created User instance.
        step2 : dict
            Cleaned data from the profile_bio step.
        step3 : dict
            Cleaned data from the farm_details step.
        """

        farmer_profile = FarmerProfile.objects.create(
            user=user,
            lga=step2.get("lga"),
        )

        farm = Farm.objects.create(
            farmer=farmer_profile,
            name=step3["farm_name"],
            lga=step3.get("farm_lga"),
            address=step3.get("farm_address", ""),
            size=step3["size"],
            primary_crop=step3.get("primary_crop"),
        )

        # M2M must be assigned after the instance has been saved.
        other_crops = step3.get("other_crops")

        if other_crops:
            farm.other_crops.set(other_crops)

    def _create_agent_records(self, user, step2):
        """
        Create ExtensionAgentProfile and mark the whitelist entry as used.

        Parameters
        ----------
        user : User
            The freshly created User instance.
        step2 : dict
            Cleaned data from the profile_bio step.
        """

        ExtensionAgentProfile.objects.create(
            user=user,
            agency_name=step2.get("agency_name", ""),
            staff_id=step2.get("staff_id", ""),
        )

        # Mark the whitelist entry so the email cannot be reused.
        ExtensionAgentWhitelist.objects.filter(email=user.email).update(is_used=True)


def farmer_required(view_func):
    """
    Decorator that restricts access to views to authenticated users with the farmer role.
    Redirects unauthenticated users to login and non-farmers to home.

    Parameters
    ----------
    view_func : callable
        The view function to be wrapped.

    Returns
    -------
    callable
        The wrapped view function enforcing farmer-only access.
    """

    def wrapper(request, *args, **kwargs):
        """
        Enforce authentication and farmer role access control.

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


@farmer_required
def farmer_profile_view(request):
    """
    Display and update the authenticated farmer's profile.

    GET renders the profile form pre-filled with existing data.
    POST validates and updates both User and FarmerProfile models.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered profile page or redirect after successful update.
    """

    profile = request.user.farmer_profile

    if request.method == "POST":
        form = FarmerProfileForm(
            request.POST,
            request.FILES,
            user=request.user,
            profile=profile,
        )
        if form.is_valid():
            form.save(user=request.user, profile=profile)
            messages.success(request, "Profile updated successfully.")
            return redirect("farmer-profile")
    else:
        form = FarmerProfileForm(user=request.user, profile=profile)

    return render(request, "profiles/farmer_profile.html", {"form": form})
